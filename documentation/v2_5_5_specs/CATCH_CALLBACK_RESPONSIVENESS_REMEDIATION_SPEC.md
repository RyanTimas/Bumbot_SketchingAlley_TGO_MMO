# Catch Callback Responsiveness — Remediation Specification

Date: 2026-10-22  
Scope: `CreatureEncounterView.catch_button_callback` and its synchronous catch, unlock, reward, image, database, and Discord dependencies.  
Primary goal: prevent one catch from freezing catch interactions on every other active creature.  
Status: implementation applied; acceptance testing and production latency measurement remain required.

## 1. Executive Summary

The current callback is an asyncio coroutine but executes substantial synchronous database, PIL/image, and domain-object work on the shared Discord event-loop thread. It then awaits a long serial chain of public Discord messages and reward checks. The per-view `asyncio.Lock` correctly protects one creature but cannot protect event-loop responsiveness across other views. The target design is a four-phase flow: **interaction gate → durable catch commit → immediate critical response → post-catch rewards/unlocks**. Only the first two phases are required before acknowledging successful catch completion. Avatar unlock checks, item rewards, image conversion for optional notifications, and optional follow-up messages must not block the event loop or delay the critical success response. Database work must not be sent concurrently through the current shared mutable `QueryHandler`; it requires serialized ownership or an explicitly isolated transaction worker.

## 2. Current Behavior and Evidence

### 2.1 Current callback chain

`CreatureEncounterView.catch_button_callback` (`src/discord/game_features/creature_enounter/CreatureEncounterView.py:45-99`) currently performs:

1. Set `catch_time` and defer the interaction (`:49-50`).
2. Check user/view eligibility (`:52-54`).
3. Acquire the per-view lock and re-check `self.caught` (`:56-67`).
4. Run synchronous `_handle_user_catch_limits` and its database calls (`:61`, `:136-141`).
5. Send a “Please wait...” follow-up (`:69-70`).
6. Run synchronous `catch_creature` (`:72`).
7. Send the public catch announcement (`:75-77`).
8. Construct `CreatureCaughtView` (`:79-80`).
9. Run three unlock checks sequentially (`:82-85`).
10. Run two item/reward checks sequentially (`:87-89`).
11. Delete the original spawn message (`:91-95`).
12. Send the final private success follow-up (`:97-98`).

### 2.2 Blocking work inside the callback

| Operation | Evidence | Blocking behavior |
|---|---|---|
| User capacity checks | `CreatureEncounterView.py:136-141` | Synchronous database calls execute on the event loop. |
| Catch profile, image/embed, insert, XP | `CatchFunctions.py:10-20` | Synchronous database, PIL/domain rendering, and writes execute before the next await. |
| Catch image conversion | `CommonFunctions.py:84-89` and `CreatureEncounterView.py:77` | Synchronous PNG encoding. |
| Event avatar checks | `AvatarUnlockHandler.py:23-30` | Synchronous database lookup/write before each awaited message. |
| Quest avatar checks | `AvatarUnlockHandler.py:32-70` | One synchronous query per avatar plus incorrectly nested batch work. |
| Special quest check | `AvatarUnlockHandler.py:72-84` | Synchronous conversion/database work around an awaited notification. |
| Milestone reward | `ItemUnlockHandler.py:11-40` | Synchronous count, inventory queries, writes, and image conversion. |
| Random reward | `ItemUnlockHandler.py:43-55` | Synchronous inventory queries/writes and image conversion when selected. |
| Retry wrapper | `CommonDecorators.py:18-35` | Wraps the entire callback and can repeat side effects after an SSL failure. |
| Shared DB connection state | `QueryHandler.py:7-15`, `:29-46` | `conn` and `cursor` are mutable handler fields; unrestricted concurrent worker calls are unsafe. |

### 2.3 Current grade

**Catch callback responsiveness: F.** One callback can monopolize the event-loop thread for the duration of all synchronous stages. The reported approximately 15-second delay is consistent with the serial sum of database, image, Discord, and reward work, but production timing must be measured by stage.

## 3. Target Contracts

### 3.1 Responsiveness contract

- The callback must acknowledge/reject the interaction promptly after the initial gate.
- After the durable catch commit succeeds, the user must receive the critical success response without waiting for optional unlock/reward notifications.
- No synchronous database query, database write, PIL encoding, image construction, or filesystem-backed image load may execute directly on the shared event-loop thread after the gate.
- A delayed reward or notification for user A must not prevent user B from pressing Catch on another active encounter.
- The implementation must preserve one-catch-wins behavior for a single encounter.

### 3.2 Correctness contract

- Capacity and interaction ownership checks occur before the durable catch commit.
- A catch commit must produce a durable `catch_id` before the success result is reported.
- XP must be applied exactly once for a successful catch.
- Optional avatar/item rewards must be idempotent and recoverable after a worker failure.
- A Discord retry must never repeat a non-idempotent catch or XP write.
- Current user-facing catch content, creature identity, environment, rarity, and catch result remain unchanged.

### 3.3 Discord interaction contract

- The initial interaction response is deferred once at `CreatureEncounterView.py:50`.
- All later user messages use follow-ups; no later path may attempt a second initial response.
- The “Please wait...” response is optional in the target design. If retained, it must not be required before the catch transaction can proceed.
- The final critical success response is sent after durable catch commit and after the `CreatureCaughtView` dependencies are available.
- Optional reward notifications may arrive after the final success response only if the product accepts the ordering change. This is an explicit decision below.

## 4. Target Phase Model

### Phase 0 — Interaction gate (must remain fast)

**Current location:** `CreatureEncounterView.py:49-67`, `_handle_user_catch_limits` at `:136-141`.

Required behavior:

1. Set the catch timestamp and defer the interaction.
2. Validate that this user may interact with the view.
3. Acquire the per-view lock only long enough to claim the encounter.
4. Re-check `self.caught` inside the lock.
5. Perform capacity validation.
6. Mark the encounter claimed in memory and/or persist an idempotent claim key.
7. Release the lock before expensive catch, image, database, or Discord work.

The gate must not hold `self.interaction_lock` while executing the catch transaction or rewards. The current lock release before line `:69` is directionally correct; the expensive work must additionally leave the event loop.

### Phase 1 — Durable catch commit (critical path)

**Current location:** `CatchFunctions.py:10-20`.

Create a catch service with an explicit result contract:

```text
CatchCommitResult:
    status: SUCCESS | ALREADY_CLAIMED | CAPACITY_REJECTED | FAILED
    catch_id: int | None
    user_profile/display data
    catch_embed data or render inputs
    catch_image data or render inputs
    total_xp: int
    reward_context/correlation id
```

The commit must atomically or idempotently cover:

- catch row insertion (`CatchFunctions.py:19`);
- XP update (`CatchFunctions.py:20`);
- encounter/catch claim identity.

The current profile query and synchronous embed generation at `CatchFunctions.py:12-16` must be moved behind the chosen blocking-work boundary. If catch rendering is not required for persistence, persist first and render the public result immediately afterward using the worker boundary.

**Important:** `catch_creature` currently returns a dictionary and is called by the AFK path in `CreatureSpawnerHandler.py:355` as well as this callback. Preserve that public return shape or introduce an adapter so the AFK path is not silently broken.

### Phase 2 — Critical user-visible completion

After Phase 1 returns success:

1. Send the public catch announcement using the existing catch embed/image (`CreatureEncounterView.py:75-77`), or define public announcement failure handling explicitly.
2. Construct `CreatureCaughtView` after `catch_id` and the successful message are available (`:79-80`).
3. Send the final private success follow-up (`:97-98`) without waiting for optional avatar/item processing.
4. Delete the original encounter message either immediately before the final response or as a separately tracked Discord operation, preserving the intended one-catch-wins behavior.

**Recommended ordering:** durable catch → public announcement → delete original encounter → final private success follow-up. If public announcement fails after the durable commit, do not rerun the complete catch callback; record/report the announcement failure and continue with the private result where Discord permits.

### Phase 3 — Post-catch rewards and unlocks

Run after the critical response through a controlled worker/task boundary:

- `check_for_event_avatars` (`AvatarUnlockHandler.py:23-30`)
- corrected `check_for_quest_avatars` (`:32-70`)
- `check_for_special_quest_avatars` (`:72-84`)
- `check_for_milestone_catch_rewards` (`ItemUnlockHandler.py:11-40`)
- `check_for_random_item_catch_reward` (`:43-55`)

Each operation must have a correlation ID containing at least user ID, creature/catch ID, and attempt number. Failures must be logged and recoverable without replaying the catch or XP write.

## 5. Safe Parallelism and Required Ordering

### 5.1 Dependency graph

```text
interaction defer
    ↓
per-view claim + capacity validation
    ↓
durable catch + XP commit
    ↓
public catch announcement ─────┐
    ↓                          │
original-message deletion       │
    ↓                          │
final private success response  │
                               │
                               └── post-catch reward/unlock worker
                                       ├── event avatar processing
                                       ├── quest avatar processing
                                       ├── special quest processing
                                       ├── milestone reward processing
                                       └── random reward processing
```

### 5.2 Operations that must remain ordered

| Before | After | Reason |
|---|---|---|
| Interaction defer | Any follow-up | Discord interaction protocol. |
| Capacity/claim | Catch insert | Prevent over-capacity or duplicate catches. |
| Catch insert | XP update/result | XP must correspond to a durable catch. Prefer one transaction or idempotent commit. |
| Catch ID and catch result | `CreatureCaughtView` construction | View requires catch-specific identifiers/message. |
| Public catch result | Final success response | The user should not be told success before the core catch result exists. |
| Catch commit | Any optional reward | Rewards must be attributable to a durable catch. |
| Reward decision | Reward write | Avoid granting an item before the decision is durable. |
| Reward write | Reward notification | Do not announce a reward that failed to persist. |

### 5.3 Operations that may be logically parallel

The following may be parallel **only after the catch commit and only with safe database ownership**:

- Event-avatar eligibility and item-reward eligibility reads.
- Quest-avatar eligibility evaluation and special-quest evaluation, if both have isolated/idempotent writes.
- Independent Discord reward notifications, if notification ordering and rate limits are explicitly defined.
- Image conversion for independent optional reward notifications, if each conversion owns its image data.

Do not implement this as unrestricted `asyncio.gather` over the current helper functions. Those helpers perform synchronous DB operations through a shared mutable `QueryHandler` and send user-visible messages. First refactor them into worker-safe operations with explicit result objects; then choose serialized or bounded parallel execution.

### 5.4 Recommended initial parallelism policy

For the first implementation, use **logical parallelism with serialized database ownership**:

1. Run eligibility calculations in one controlled worker transaction or queue.
2. Produce a list of idempotent reward commands.
3. Apply reward writes in deterministic order.
4. Send notifications after each successful write, or consolidate them into one follow-up.

This may not maximize raw throughput, but it removes event-loop blocking without introducing SQLite races or notification storms. A later bounded worker pool requires **APPROVAL REQUIRED** after database connection ownership is redesigned.

## 6. Database and Blocking-Work Boundary

### 6.1 Current limitation

`QueryHandler` stores one mutable `conn` and `cursor` on the handler (`QueryHandler.py:7-15`) and opens/closes them per operation (`:29-46`). The global database handler is shared by feature code. Calling multiple database functions concurrently with `asyncio.to_thread` would risk connection/cursor interference and transaction interleaving.

### 6.2 Approved implementation options

Choose one and document the choice before implementation:

| Option | Contract | Approval |
|---|---|---|
| Serialized database worker | One queue/worker owns database operations and transaction boundaries; callbacks await results. | Uses an existing concurrency model only if already present; otherwise **APPROVAL REQUIRED** for new queue infrastructure. |
| Per-operation isolated connection | Each worker operation creates and owns its SQLite connection; no shared `conn`/`cursor`; transaction scope is explicit. | No external dependency; requires database-layer implementation and load testing. |
| Existing executor with serialized calls | Reuse the current executor pattern but guard database ownership so only one transaction touches the shared handler at a time. | No external dependency; may limit throughput. |
| Unrestricted `asyncio.to_thread`/`gather` | Concurrent calls against current shared handler. | **NOT APPROVED**; unsafe with current mutable connection fields. |

PIL/image work may use the same controlled blocking boundary, but image objects must not be mutated concurrently or shared without copying.

### 6.3 Transaction/idempotency requirements

- Add an encounter claim key or equivalent durable uniqueness rule before retrying catch orchestration.
- Replaying the same encounter must return the existing `catch_id`, not insert another creature.
- XP update must be coupled to catch identity or guarded so it cannot be applied twice.
- Avatar link insertion must tolerate an existing link.
- Inventory reward application must be idempotent by `(catch_id, reward_type, reward_key)` or equivalent durable record.
- Worker retries operate from `catch_id`; they never rerun the entire interaction callback.

If the schema cannot support these guarantees without a migration, mark the migration **APPROVAL REQUIRED** and do not simulate idempotency only in memory.

## 7. Reward and Unlock Refactoring Contracts

### 7.1 `check_for_quest_avatars`

**Evidence:** `AvatarUnlockHandler.py:37-70`.

The current batch collection/check/insert/notification block is nested inside the avatar evaluation loop. The replacement must:

1. Evaluate every unlockable avatar (`:39-44`).
2. Collect eligible parent children and direct avatars once (`:46-55`).
3. Return success with no work only after all candidates are evaluated.
4. Batch-check existing avatar IDs once (`:59-61`).
5. Batch-insert new links once (`:63-66`).
6. Produce notification commands only for newly inserted links (`:68-70`).

### 7.2 Item rewards

**Evidence:** `ItemUnlockHandler.py:11-55`.

Split synchronous eligibility/read logic from notification/image conversion. Reward helpers should return durable reward results rather than directly sending all Discord messages. Preserve milestone thresholds, random reward probability, quantities, and user-visible text.

### 7.3 Notification policy

Select one:

- **Individual notifications:** preserve current messages but send only after durable writes; apply a bounded notification queue.
- **Consolidated notification:** combine rewards into one ephemeral response after all writes; changes current message count/content and requires product approval.
- **Eventual notifications:** send through a post-catch worker; failures are retried independently and do not block catch success.

The recommended first implementation is individual notifications through a bounded post-catch worker, with failures logged and retryable.

## 8. Retry and Failure Semantics

### 8.1 Current risk

`retry_on_ssl_error` wraps the entire callback (`CreatureEncounterView.py:46-48`; decorator implementation `CommonDecorators.py:18-35`). A network error after catch insertion or reward writes can rerun non-idempotent work.

### 8.2 Required replacement

- Remove whole-callback retry around the durable catch workflow, or restrict it to the pre-commit interaction gate.
- Retry individual Discord operations only when the operation is known safe to retry.
- Retry post-catch worker stages using durable catch/reward IDs.
- Treat a database commit failure as a failed catch unless the transaction reports an existing committed idempotent result.
- Record each retry attempt and stage in logs/metrics.
- Never send a second “success” response because a later optional reward operation failed.

## 9. Observability and Success Criteria

### 9.1 Required timings

Record structured timings with a correlation ID for:

- interaction defer acknowledgement;
- gate/lock wait;
- capacity check;
- catch database transaction;
- catch image/embed generation;
- public announcement send;
- original-message deletion;
- final success follow-up;
- each post-catch reward stage;
- database wait/transaction time;
- event-loop lag during the interaction;
- retry count and failure stage.

### 9.2 Acceptance targets

The implementation is successful when a representative test demonstrates:

- Catch gate acknowledgement is not delayed by reward processing.
- Catching creature B remains responsive while creature A's reward stage is artificially delayed.
- No synchronous database/PIL operation runs on the event-loop thread during post-gate work.
- Median critical catch response improves materially from the current baseline.
- P95 critical response is bounded independently of the number of unlockable rewards.
- Duplicate clicks produce at most one durable catch and one XP award.
- A worker retry does not duplicate avatar links, item quantities, XP, or catch rows.
- Existing catch messages, creature data, capacity rules, and per-creature race behavior remain correct.

The exact millisecond target must be set after baseline instrumentation; this document does not invent a benchmark value.

## 10. Test Obligations

**Current status:** No dedicated catch responsiveness regression suite was identified. **NO EXISTING TESTS — CREATE.**

### 10.1 Unit tests

- Gate rejects unauthorized users without database catch work.
- Capacity-full users receive the existing capacity response.
- Two users clicking the same encounter produce one winner.
- Repeated clicks from one user produce one catch/XP result.
- `catch_creature` result shape remains compatible with AFK callers.
- Quest avatar evaluation processes all candidates before batching.
- Reward commands are idempotent when replayed with the same catch ID.
- Optional reward failure does not fail the durable catch.
- Discord operation failure does not replay the durable catch.

### 10.2 Async responsiveness tests

- Start catch A with a deliberately blocked reward worker.
- While catch A is blocked, submit catch B on a different view.
- Assert catch B can defer, acquire its own view lock, and reach its critical response.
- Add a delayed synchronous-operation probe to ensure the event loop is not blocked by post-catch work.
- Verify task cancellation and shutdown do not leave unobserved reward tasks.

### 10.3 Integration/load tests

Run representative workloads with zero, one, and several unlockable rewards. Capture query count, image conversion count, event-loop lag, interaction latency, duplicate writes, Discord rate-limit responses, and worker retry behavior.

## 11. Rollback Plan

Implement the new flow behind a reversible internal configuration switch or deployment flag; do not add a public command for it.

Rollback order:

1. Stop dispatching new post-catch worker jobs.
2. Drain or cancel pending optional reward jobs according to the notification policy.
3. Keep the durable catch/idempotency protections active.
4. Restore the legacy inline reward path only if its writes are protected against replay.
5. Compare catch latency and duplicate-write metrics before removing the fallback.

If no safe idempotency boundary exists, do not support a legacy fallback that can duplicate catch/XP/reward writes.

## 12. Implementation Ordering

1. Add baseline stage timing and correlation IDs without changing behavior.
2. Define the catch commit/idempotency contract and database ownership boundary.
3. Extract the critical catch service while preserving `catch_creature` compatibility.
4. Correct quest avatar batching.
5. Extract reward/unlock functions into durable result producers and notification producers.
6. Add the post-catch worker or controlled task boundary.
7. Move optional work after the critical success response.
8. Narrow retry scope away from the entire callback.
9. Add responsiveness/concurrency/load tests.
10. Enable the new flow progressively and compare metrics.

## 13. Explicit Non-Goals

- Do not redesign `CreatureSpawnerHandler` as part of this catch-specific implementation, except where its AFK caller must remain compatible with the catch service contract.
- Do not introduce unrestricted thread fan-out against the shared SQLite handler.
- Do not use `asyncio.gather` on the current reward helpers without first defining database ownership, idempotency, and notification ordering.
- Do not change catch probability, inventory capacity, reward thresholds, reward quantities, creature rarity, or user-visible text without separate approval.
- Do not make the final success response wait for optional reward notifications merely to preserve incidental current ordering.

## 14. Open Decisions

- **Product decision:** May avatar/item notifications arrive after the final success response? Recommended: yes.
- ANSWER - YES

- **Product decision:** If the public catch announcement fails after the durable catch commit, should the private success response still be sent? Recommended: yes, with a logged announcement failure.
- ANSWER - YES

- **Architecture decision:** Choose serialized database ownership, isolated per-operation connections, or an approved transaction worker before using thread offload or parallel reward processing.
- **Schema decision:** Approve an encounter/reward idempotency key or equivalent uniqueness mechanism if current tables cannot guarantee exactly-once effects.
- **Operational decision:** Set concrete P50/P95 response targets after baseline instrumentation.


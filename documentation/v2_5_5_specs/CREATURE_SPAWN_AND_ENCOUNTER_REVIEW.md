# Creature Spawning and Encounter Responsiveness Review

Date: 2026-10-23
Scope: `CreatureSpawnerHandler`, `CreatureEncounterView.catch_button_callback`, and directly called catch/unlock/reward paths.  
Method: Updated static review with source evidence, remediation-spec reconciliation, and the added regression tests. No production latency profile was available.

## 1. Executive Summary

`CreatureSpawnerHandler` now uses the intended asyncio concurrency model for scheduler ownership, creature despawn timers, and noon environment changes. The R1–R5 remediation is substantially implemented: sleeping OS threads and cross-thread `.result()` waits were removed, duplicate scheduler starts are claimed synchronously, and a private cleanup path cancels handler-owned tasks. The class still combines lifecycle orchestration, bonus interpretation, creature selection, spawn presentation, duplicate spawning, AFK capture, and environment scheduling, so separation-of-concerns concerns remain. Overall grade: **A- for the remediated timer/lifecycle model, C+ for structure, and C for spawn correctness/readability**.

The catch path is materially improved but not fully non-blocking. The critical catch, capacity checks, and reward preparation now use the serialized blocking boundary, and optional rewards are scheduled after the success response. However, `CreatureCaughtView` still performs synchronous database work during construction and in several button/modal callbacks. Those interactions can still delay acknowledgement when database or image work is slow. The original approximately 15-second event-loop starvation risk is reduced for the main catch flow, but production stage timing and focused caught-view interaction tests are still required.

The highest-value remaining work is to finish the `CreatureCaughtView` callback boundary and add task-exception observability. For the spawner, introduce explicit bonus-resolution and creature-selection boundaries while retaining `CreatureSpawnerHandler` as the lifecycle coordinator.

### Remediation status

| Remediation item | Status | Current evidence |
|---|---|---|
| R1/R2 — despawn threads and blocking sleep | Implemented | `_despawn_creature` is an asyncio task using `await asyncio.sleep`; eligible despawns are tracked in `_despawn_tasks`. |
| R3 — noon environment scheduling | Implemented | `_schedule_environment_change` calculates the existing US/Eastern noon offset and awaits it on the bot loop. |
| R4 — cross-thread Discord submission and `.result()` | Implemented for the remediated paths | Fetch, delete, and despawn notification are awaited in order; AFK notification uses same-loop task creation. |
| R5 — duplicate scheduler start window | Implemented | `_spawner_start_claimed` is set before task creation and private `_cleanup_tasks` cancels owned tasks. |
| Catch critical path | Implemented with residual risk | `catch_creature_async`, capacity checks, and reward preparation use `run_serialized_blocking`; caught-view callbacks still contain direct blocking work. |
| Whole-callback retry removal | Implemented | The catch callback no longer retries the complete non-idempotent orchestration. |
| Quest-avatar batching | Implemented | Quest candidates are collected and batch-processed outside the per-avatar evaluation loop. |

## 2. Grades

| Area | Grade | Reason |
|---|---:|---|
| Spawner lifecycle/task ownership | A- | Synchronous start claim, task handles, tracked despawns, and private cancellation cleanup address the prior duplicate-start and sleeping-thread risks; task exception inspection remains incomplete. |
| Spawner separation of concerns | C+ | One class owns startup, scheduling, bonus policy, selection, presentation, duplicates, AFK capture, and environment changes. |
| Active-bonus handling | C | Bonuses are loaded once and interpreted in several methods with implicit precedence and mixed responsibilities. |
| Creature selection | C+ | Selection supports kingdom/rarity fallback, but selection, rarity mutation, and spawn-time calculation are coupled and `None` handling is unsafe. |
| Despawn/environment coordination | A- | Despawn and environment waits no longer consume sleeping OS threads, and same-loop Discord operations preserve ordering; AFK/database/image work can still block the loop. |
| Catch callback responsiveness | B- | Critical catch/capacity/reward preparation is serialized off-loop and optional rewards run after the success response, but caught-view construction and later component callbacks still do synchronous DB/PIL work. |
| Catch concurrency isolation | C+ | The per-view lock still protects one creature and the main catch path no longer monopolizes the loop for all DB/PIL work; caught-view callback blocking can still affect unrelated interactions. |
| Catch/reward reliability | B- | Whole-callback retry was removed and post-catch failures are logged, but reward writes/notifications remain independently partial and idempotency is not established. |
| Observability | D+ | No stage timing exists around catch DB, image, unlock, reward, and Discord operations; a generic execution timer cannot identify the bottleneck. |

## 3. Current Runtime Flow

### 3.1 Spawner flow

1. `DiscordBot.on_ready` calls `start_creature_spawner` (`src/discord/DiscordBot.py:88-101`).
2. `start_creature_spawner` synchronously claims lifecycle ownership before creating the spawn loop plus environment scheduler; repeated calls before the tasks yield are no-ops (`CreatureSpawnerHandler.py:88-107`).
3. `_creature_spawner` resolves bonus effects, calls `spawn_creature`, processes post-spawn events, and waits on the existing event/timeout (`CreatureSpawnerHandler.py:164-197`).
4. `spawn_creature` selects or accepts a creature, applies the mythical check, builds/sends the encounter, schedules an asyncio despawn task for eligible rarities, and may recursively create swarm duplicates (`CreatureSpawnerHandler.py:202-219`, `:222-235`).
5. `creature_picker` filters the pool, applies rarity fallback, deep-copies the selection, changes mythical rarity when needed, and calculates despawn timing (`CreatureSpawnerHandler.py:263-298`).
6. The handler also owns AFK trap capture, day/night changes, environment polling, and noon environment application. The environment transition is now an asyncio task and wakes the spawn loop through the existing `spawn_event` (`CreatureSpawnerHandler.py:396-471`).

### 3.2 Catch flow

`catch_button_callback` performs the following (`CreatureEncounterView.py:54-119`):

1. Defers the interaction and checks the per-view interaction lock (`:49-67`).
2. Performs the capacity check through `run_serialized_blocking` (`:70-75`).
3. Sends a short pending response, then calls `catch_creature_async`, which serializes the synchronous catch/profile/image/DB work off the event-loop thread (`:78-89`, `CatchFunctions.py`).
4. Sends the public catch message and constructs `CreatureCaughtView` on the event-loop thread (`:91-104`). The constructor still performs a synchronous profile lookup and view-state DB reads.
5. Deletes the original spawn message and sends the final private success response before optional rewards (`:106-113`).
6. Runs avatar and item reward checks in a tracked background task after the critical response (`:115-119`, `:158-169`).

The main callback no longer performs all blocking database/image work inline, but it still mixes network waits with event-loop-thread view construction and retains a serial reward worker. `CreatureCaughtView` component callbacks remain a separate responsiveness boundary.

## 4. CreatureSpawnerHandler Findings

### S1 — Lifecycle orchestration is too broad (C+)

**Evidence:** `CreatureSpawnerHandler.py:85-159`, `:164-197`, `:378-471`.

`start_creature_spawner`, `_scheduler_task_completed`, `_cleanup_tasks`, and `_creature_spawner` are lifecycle responsibilities, but the same class also implements selection, bonus policy, presentation, AFK capture, day/night state, and environment transitions. This makes changes difficult to reason about because a change to selection can affect task ownership, and a change to environment state can affect despawn presentation.

**Recommended boundary:** Keep `CreatureSpawnerHandler` as a thin coordinator with these explicit collaborators or private service boundaries:

| Responsibility | Recommended boundary | Current methods |
|---|---|---|
| Task/lifecycle ownership | `SpawnerLifecycle` or clearly grouped private lifecycle methods | `start_creature_spawner`, `_cleanup_tasks`, callbacks |
| Bonus policy | `SpawnBonusResolver` returning an immutable spawn decision/context | `get_spawn_bonus_effects`, parts of `get_creature_rarity`, `perform_mythical_check` |
| Creature selection | `CreatureSelectionService` returning a fully prepared spawn candidate | `creature_picker`, rarity fallback, despawn-time preparation |
| Spawn presentation | `CreatureSpawnService` or a narrow presentation method | embed construction, channel send, encounter view creation in `spawn_creature` |
| Duplicate policy | `SwarmSpawnPolicy` or a small private method | `_duplicate_creature_spawner` |
| Environment lifecycle | `EnvironmentChangeService` or separate scheduler owner | `:378-471` |
| AFK capture | Existing catch/trap service boundary | `handle_afk_trap_catch` |

Do not split into classes merely to move lines. Each boundary should have a small input/output contract and be testable without constructing the Discord bot.

### S2 — Active bonuses are loaded once and interpreted in multiple places (C)

**Evidence:** `CreatureSpawnerHandler.py:45`, `:172-176`, `:263-298`, `:313-330`.

`active_bonuses` is loaded once during initialization (`:45`). It is then consumed by the spawn loop for charm interval selection (`:172-176`), by `get_spawn_bonus_effects` for kingdom/rarity selection (`:313-330`), and by `perform_mythical_check` (`:290-311`). The same spawn decision is therefore distributed across multiple methods.

Specific readability/correctness concerns:

- `get_spawn_bonus_effects` overwrites `kingdom` and `rarity` as it iterates bonuses. If multiple bonuses are present, precedence is implicit in collection order rather than expressed as policy (`:318-330`).
- `perform_mythical_check` treats `user_bonus_active` as truthy rather than representing a specific user bonus decision (`:290-306`); `spawn_creature` passes the entire `user` object (`:206`).
- Charm effects, mythical odds, rarity fallback, and interval shortening are not represented by one inspectable spawn decision.
- The one-time load is intentional according to the remediation decisions, but it means bonus changes after handler initialization are not reflected.

**Recommended design:** Resolve an immutable `SpawnBonusContext` once per spawn attempt containing:

- selected kingdom, if any;
- requested/preferred rarity, if any;
- mythical eligibility and odds modifier;
- interval modifier;
- source bonus IDs for diagnostics.

Then pass that context into selection and mythical evaluation. Keep active-bonus freshness unchanged unless separately approved; the improvement is centralization and explicit precedence, not a silent refresh.

### S3 — Selection and spawning are coupled (C+)

**Evidence:** `CreatureSpawnerHandler.py:202-218`, `:263-298`.

`creature_picker` does more than choose a candidate: it applies fallback rarity policy, deep-copies the object, mutates mythical rarity, and refreshes spawn/despawn time (`:263-298`). `spawn_creature` then applies another mythical check, creates embeds/views, sends Discord files, starts despawn, and recursively starts duplicates (`:202-218`).

This makes it difficult to answer a basic question such as “what will spawn?” without also considering message side effects and task creation.

**Recommended design:** Use a pure-ish selection contract:

```text
SpawnCandidate = {
    creature,
    selected_rarity,
    is_mythical,
    spawn_time,
    despawn_delay,
    bonus_context,
}
```

Selection should not send Discord messages or create tasks. Presentation should receive the candidate and perform only rendering/send work. Preserve current fallback ordering and rarity probabilities in regression tests.

**Correctness edge case:** `creature_picker` can return `None` when a requested kingdom has no candidates (`:185-188`), while `spawn_creature` immediately dereferences `creature.local_rarity` (`:204-206`). Callers currently try to guard some bait cases, but the handler itself should define a safe no-candidate contract rather than relying on every caller.

### S4 — Duplicate spawning is recursive and can multiply work (C+)

**Evidence:** `CreatureSpawnerHandler.py:220-234`.

`_duplicate_creature_spawner` recursively calls `spawn_creature`, and each duplicate can perform embed construction, Discord sends, task creation, and another duplicate decision. The probability is bounded in normal conditions, but the work is not represented as a batch or explicit cap.

**Recommendation:** Preserve probability and observable swarm behavior, but add a configured maximum chain safety bound and expose duplicate count in diagnostics. If the cap would change gameplay, mark it as a product decision rather than silently adding it.

### S5 — Remaining synchronous work inside async paths (C)

**Evidence:** `CreatureSpawnerHandler.py:333-363`, `:421-471`.

The timer redesign removes thread-per-creature waits, and the interactive catch path now serializes its legacy database/PIL work. However, AFK handling still performs synchronous database reads/writes and synchronous catch/image work from the despawn task (`:346-358`). Environment transition still builds images synchronously before an awaited Discord send (`:442-463`). These operations can still block the event loop even though the timer itself is non-blocking.

**Recommendation:** Measure and isolate blocking DB/image work before moving it to threads. The existing shared query handler stores mutable `conn`/`cursor`, so an arbitrary `asyncio.to_thread` around concurrent database calls is not automatically safe. Use a serialized database worker/transaction boundary or refactor the query layer before broad offloading.

### S6 — Task completion and failure visibility are incomplete (C+)

**Evidence:** `CreatureSpawnerHandler.py:104-127`, `:130-159`, `:213-216`.

Task callbacks now remove completed scheduler and despawn task references, and `_cleanup_tasks` cancels handler-owned scheduler/despawn tasks. The callbacks still do not inspect task exceptions. AFK notification tasks created at `:357` are detached from `_despawn_tasks`, so shutdown cleanup does not wait for or cancel them. A failed detached notification can therefore still become an unobserved task exception.

**Recommendation:** Extend the existing completion callbacks to call `task.exception()` for non-cancelled tasks and log failures with creature/message identifiers. Either track AFK notification tasks in the private cleanup set or explicitly register a best-effort completion callback that logs failures.

## 5. CreatureEncounterView Findings

### E1 — Blocking work remains in caught-view interactions (B-)

**Evidence:** `CreatureEncounterView.py:45-99`, `CatchFunctions.py:10-20`.

The original catch callback starvation was reduced by the implementation, but the callback and the view it creates still have synchronous sections:

- `catch_creature_async` delegates the synchronous profile/embed/image/catch/XP operation through `run_serialized_blocking` (`CatchFunctions.py`).
- Capacity checks and reward preparation use the same serialized boundary (`CreatureEncounterView.py`, `AvatarUnlockHandler.py`, `ItemUnlockHandler.py`).
- `CreatureCaughtView.__init__` performs a synchronous profile lookup and builds display-slot state on the event-loop thread (`CreatureCaughtView.py:13-45`).
- Caught-view buttons and modal callbacks still call synchronous database and image/release methods after acknowledgement (`CreatureCaughtView.py:64-142`, `:179-184`).
- Optional avatar/item rewards are scheduled after the success response, but remain serial within `_process_post_catch_rewards` (`CreatureEncounterView.py:158-169`).

The critical catch operation is no longer expected to monopolize the event loop for its full DB/PIL duration. Nevertheless, a slow caught-view constructor or component callback can still delay unrelated interactions. The previous F grade is therefore no longer accurate for the main catch path, but the full interaction experience is not yet fully non-blocking.

**Remaining action:** Move caught-view database reads and release/favorite/nickname/display operations behind the serialized blocking boundary while keeping Discord `View` and component mutation on the event-loop thread. Add interaction tests that assert acknowledgement occurs before blocking work completes.

### E2 — The per-view interaction lock does not provide global responsiveness (D)

**Evidence:** `CreatureEncounterView.py:34`, `:52-67`.

The lock correctly serializes competing interactions for one creature and `self.caught` provides a second check (`:64-76`). The lock is released before the catch commit and reward chain begins, which avoids a long lock hold. It does not prevent event-loop blocking from caught-view callbacks or detached reward work; a lock change alone is not a substitute for the serialized blocking boundary.

### E3 — Post-catch operations remain serial within a background task (B-)

**Evidence:** `CreatureEncounterView.py:72-98`.

The critical callback now sends the success response before waiting for avatar/item rewards. The background worker still awaits event-avatar, quest-avatar, special-quest, milestone, and random-item checks serially (`CreatureEncounterView.py:158-169`). This preserves notification order and avoids unrestricted concurrent access to the shared database handler, but it delays optional notifications when an earlier reward stage is slow.

**Recommendation:** Define phases:

1. **Critical catch phase:** validate ownership/capacity, persist catch and XP, and send the public catch announcement.
2. **Immediate user response:** send the final success response as soon as the critical phase succeeds.
3. **Post-catch rewards:** process avatar/item unlocks through a controlled background task or serialized worker, with idempotent writes and explicit notification policy.

The phase separation tradeoff has been accepted: optional rewards are eventual and may complete after the critical success response. Do not replace the serialized worker with unrestricted `asyncio.gather` until database connection ownership and notification ordering are explicitly redesigned.

### E4 — Whole-callback retry can repeat side effects (Resolved)

**Evidence:** `CreatureEncounterView.py:46-48`, `src/commons/CommonDecorators.py:18-35`.

The catch callback no longer has `retry_on_ssl_error` around the complete orchestration. Network/API failures are handled at narrower points, and a failed public announcement is logged without replaying the durable catch commit. Narrow retries remain in some individual component/reward callbacks and should continue to be reviewed for idempotency.

**Status:** The original finding is resolved for `catch_button_callback`; preserve this boundary in future changes.

### E5 — Quest unlock batching was incorrectly nested (Resolved)

**Evidence:** `AvatarUnlockHandler.py:37-70`.

Quest avatar eligibility is now evaluated first, followed by one batch existing-link check, one batch insert, and notification construction (`AvatarUnlockHandler.py`). The prior early-return/repeated-batch behavior is no longer present.

**Status:** The recommended batching structure has been implemented; retain the multi-avatar regression test as a guard against reintroducing the nested loop.

## 6. Why the Callback Can Take 15 Seconds

The static evidence supports several additive contributors:

| Stage | Evidence | Likely cost |
|---|---|---|
| Catch profile + embed + image + DB writes | `CatchFunctions.py`, `AsyncBlocking.py` | SQLite connection/query overhead, PIL rendering, disk/image work; now serialized off the event-loop thread |
| Public catch send | `CreatureEncounterView.py:75-77` | Discord network/API latency |
| Event avatar checks | `AvatarUnlockHandler.py:23-30` | DB query plus one notification per unlock |
| Quest avatar checks | `AvatarUnlockHandler.py` | One query per avatar remains, but batch existing-link/insertion work is no longer nested |
| Special quest check | `AvatarUnlockHandler.py:72-84` | Image conversion, notification, DB insert when triggered |
| Milestone reward | `ItemUnlockHandler.py:11-40` | Full user-creature count, multiple inventory reads/writes, up to three image notifications |
| Random reward | `ItemUnlockHandler.py:43-55` | Inventory reads/writes and image conversion when selected |
| Caught-view construction/callbacks | `CreatureCaughtView.py:13-184` | Synchronous profile, display, favorite, release, nickname, and image/database work can still delay component interactions |
| Spawn deletion/final response | `CreatureEncounterView.py:106-113` | Discord API latency; critical response is sent before optional rewards |
| Narrow callback retries | `CreatureCaughtView.py`, reward handlers | Individual retries can still amplify a component/reward operation if its write is not idempotent; the whole catch is no longer retried |

The critical callback's response time is now separated from optional reward processing, and the largest catch DB/PIL stage is offloaded through a serialized worker. Synchronous caught-view callbacks and AFK/environment image/database work can still block the event loop, so the system should not yet be described as completely non-blocking.

**Required measurement:** Add stage timings around `catch_creature`, each unlock/reward function, message send/delete, image conversion, and database transaction boundaries. Record correlation fields such as user ID, creature ID, catch ID, and attempt number without logging sensitive tokens.

## 7. Prioritized Improvement Plan

### P0 — Finish event-loop responsiveness

1. Keep the initial interaction defer and per-view race protection.
2. Move `CreatureCaughtView` profile loading and callback database/image/release work behind `run_serialized_blocking`, while creating and mutating Discord UI objects on the event-loop thread.
3. Keep the success response before optional unlock notifications; this accepted tradeoff is now implemented.
4. Add idempotency and failure visibility for post-catch reward writes and detached notifications.

### P1 — Reduce catch work

1. Add stage timing around the serialized catch/reward worker and caught-view callbacks.
2. Batch profile/inventory/reward reads instead of issuing one connection per query; coordinate with the database remediation specification.
3. Avoid converting unlock images until a notification is actually going to be sent.
4. Keep Discord retries narrowly scoped rather than retrying the entire callback.

### P2 — Improve spawner readability and correctness

1. Introduce an explicit immutable bonus decision/context used by interval selection, rarity selection, and mythical evaluation.
2. Separate candidate selection from Discord presentation and task registration.
3. Define and test the no-candidate contract for `creature_picker`/`spawn_creature`.
4. Add task exception logging and track detached AFK notification tasks in private cleanup.
5. Add a bounded/observable swarm policy without changing probability unless approved.

### P3 — Measure and tune

1. Add structured per-stage timings before changing concurrency further.
2. Capture event-loop lag or callback duration during a synthetic multi-creature workload.
3. Compare catch latency with zero, one, and several unlockable rewards.
4. Verify that catching creature A remains responsive while creature B's database/image/reward work is deliberately delayed.

## 8. Recommended Target Design

```text
DiscordBot
  └── CreatureSpawnerHandler (lifecycle coordinator)
        ├── SpawnBonusResolver -> SpawnBonusContext
        ├── CreatureSelectionService -> SpawnCandidate
        ├── SpawnPresentationService -> Discord message/view
        ├── DespawnTaskRegistry
        └── EnvironmentScheduler

CreatureEncounterView
  ├── CatchGate (defer + per-creature ownership/capacity check)
  ├── CatchService (idempotent durable catch transaction)
  ├── Immediate response service (public/private critical messages)
  └── PostCatchRewardWorker (avatar/item checks and notifications)
```

The target is not to make every function asynchronous. The target is to keep blocking database/PIL work out of the shared event-loop thread, preserve per-creature correctness, and make user-visible critical completion independent from optional reward processing.

## 9. Open Questions and Tradeoffs

- **RESOLVED:** Optional avatar/item unlock notifications may complete after the final success response; the background reward task is the accepted ordering tradeoff.
- **NEEDS REVIEW:** Can catch and reward writes be made idempotent using existing catch IDs/user-creature uniqueness rules?
- **REQUIRES TRADEOFF:** Offloading synchronous database work to threads improves event-loop responsiveness but requires safe connection ownership; the current shared `QueryHandler` is not a safe arbitrary-concurrency boundary.
- **NEEDS REVIEW:** Should the spawner treat no eligible creature as a normal skipped spawn or a logged operational error?
- **NEEDS REVIEW:** Should multiple active kingdom/rarity bonuses stack, choose highest priority, or use current iteration-order behavior?
- **RESOLVED:** A private `_cleanup_tasks` path cancels handler-owned scheduler/despawn tasks on shutdown; detached AFK notification tasks still need either registration in that cleanup set or explicit best-effort exception logging.
- **NEEDS REVIEW:** Should caught-view database and image work be moved behind the same serialized boundary before the responsiveness remediation is considered complete?
- **Residual limitation:** This review remains static with respect to production latency. The exact remaining split among SQLite, PIL, Discord, AFK handling, and caught-view/reward work requires stage timing in a representative runtime.


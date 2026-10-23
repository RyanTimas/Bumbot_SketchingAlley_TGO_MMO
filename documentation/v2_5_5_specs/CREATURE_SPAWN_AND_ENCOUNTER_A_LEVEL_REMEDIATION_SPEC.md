# Creature Spawning and Encounter Pipeline — A-Level Remediation Specification

**Status:** implementation partially applied; task observability and caught-view blocking-work isolation are implemented and tested. Schema-dependent catch/reward idempotency, production measurements, and remaining A-level closure work are not yet applied.

## 1. Purpose

Close the remaining sub-A findings in `CREATURE_SPAWN_AND_ENCOUNTER_REVIEW.md` and move the creature spawning and encounter pipeline toward A-level reliability, responsiveness, separation of concerns, and observability.

This is one coordinated specification for the remaining implementation work. It must be applied incrementally, with tests and measurements after each phase. The implementation must preserve the behavior already accepted by the previous remediation work unless this specification explicitly identifies a separate product decision.

Primary source files:

- `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py`
- `src/discord/game_features/creature_enounter/CreatureEncounterView.py`
- `src/discord/game_features/creature_enounter/CreatureCaughtView.py`
- `src/discord/game_features/creature_enounter/CatchFunctions.py`
- `src/discord/handlers/AvatarUnlockHandler/AvatarUnlockHandler.py`
- `src/discord/handlers/ItemUnlockHandler/ItemUnlockHandler.py`
- `src/commons/AsyncBlocking.py`

Required final documentation target:

- `documentation/v2_5_5_specs/CREATURE_SPAWN_AND_ENCOUNTER_REVIEW.md`

## 2. Current Baseline

The following work is already implemented and must be preserved:

- Async despawn timers use event-loop tasks instead of sleeping OS threads.
- Noon environment changes use an asyncio task and preserve the existing `spawn_event` wakeup.
- Cross-thread `.result()` waits and the remediated `run_coroutine_threadsafe` paths were removed.
- Scheduler start ownership is claimed before task creation.
- Handler-owned scheduler and despawn tasks have private cleanup support.
- Interactive catch database/PIL work uses the serialized blocking boundary.
- Optional reward work runs after the critical success response.
- Whole-callback retry was removed from `catch_button_callback`.
- Quest-avatar evaluation and batch insertion were moved out of the nested per-avatar write loop.
- `SpawnBonusContext`, `SpawnCandidate`, selection/preparation helpers, duplicate-policy helpers, and the no-candidate guard exist.
- Spawner regression tests cover the current lifecycle, selection, no-candidate, and mythical/transcendant behavior.

The following work from this specification has now been applied:

- Scheduler, despawn, environment, and AFK notification task failures are consumed and logged without treating cancellation as an error.
- AFK notification tasks are tracked by the spawner and included in private cleanup.
- Caught-view profile/display state is preloaded through `run_serialized_blocking` before UI construction in the interactive catch path.
- Analyze, storage expansion, favorite, display selection, nickname persistence/embed generation, and release-result image generation use the serialized blocking boundary after prompt acknowledgement.
- Release database preparation uses the shared serialized blocking boundary rather than an unsynchronized executor.
- Focused lifecycle and catch-responsiveness regression tests cover the applied task-ownership behavior.

The following areas remain below A level or are not yet proven at A level:

| Area | Current grade/status | Main remaining issue |
|---|---|---|
| Spawner separation of concerns | B- | The handler still owns lifecycle, policy, selection, presentation, AFK, and environment responsibilities. |
| Active-bonus handling | B- | Context resolution exists, but all decision inputs are not carried through one complete typed pipeline and precedence remains compatibility-only behavior. |
| Creature selection | B | The public picker remains a compatibility wrapper around an internal candidate result; presentation and selection still share coordinator state. |
| Catch callback responsiveness | B- | `CreatureCaughtView` construction and component callbacks still perform synchronous database/image/release work. |
| Catch concurrency isolation | C+ | Per-view locking does not cover stale views, duplicate workers, or all caught-view state mutations. |
| Catch/reward reliability | B- | Writes and notifications are not proven idempotent across retries, replay, timeout, or process restart. |
| Observability | D+ | There is no complete stage timing, event-loop lag measurement, task failure logging, or reward recovery telemetry. |
| AFK/environment blocking work | C | Synchronous database/catch/image operations remain in async spawner paths. |

## 3. A-Level Definition

The pipeline may be graded A-level only when all applicable criteria below are demonstrated by tests and representative runtime measurements.

### 3.1 Responsiveness thresholds

The exact production thresholds may be adjusted after a baseline measurement, but the implementation must establish numeric limits before final grading:

- Every Discord component/modal interaction acknowledges within **1 second** in representative tests under delayed database/image work.
- The critical catch response is sent without waiting for optional reward notifications.
- No synchronous database or PIL operation executes on the shared Discord event-loop thread in the caught-view, catch, AFK, or environment paths.
- Representative event-loop lag remains below **100 ms p95** and **250 ms p99** during a multi-encounter workload with delayed blocking operations isolated in the serialized boundary.
- A slow optional reward stage does not prevent another encounter or caught-view interaction from being acknowledged.

If production infrastructure cannot measure these exact values, the test harness must use controlled delays and report the equivalent stage timings.

### 3.2 Reliability thresholds

- Replaying the same catch operation never creates a second creature catch.
- Replaying any individual reward stage never grants the same reward twice.
- Notification retries never repeat a durable grant.
- A process restart leaves durable catch/reward state recoverable without manual database repair.
- Every owned asyncio task either completes, is cancelled during private cleanup, or reports a classified failure.
- No unhandled task exception is emitted for handler-owned tasks.

### 3.3 Architectural thresholds

- Lifecycle, bonus resolution, selection, presentation, duplicate policy, AFK processing, and environment scheduling have explicit contracts.
- Each blocking boundary has a single owner and documented serialization rule.
- Public compatibility wrappers remain stable unless a migration plan explicitly changes them.
- No helper silently changes gameplay probabilities, fallback order, or message ordering.

## 4. Compatibility and Non-Goals

### 4.1 Locked compatibility behavior

The implementation must preserve:

- One-time loading of `active_bonuses` unless a separate product decision approves refresh behavior.
- Existing kingdom and rarity bonus activation probabilities.
- Existing iteration-order overwrite behavior, including failed activation resets, until explicit precedence policy is approved.
- Existing rarity fallback order.
- Existing transcendant mythical bypass.
- Existing mythical odds, ultra-charm behavior, and duplicate-chain multiplier behavior.
- Existing supplied-creature behavior.
- Existing duplicate probabilities and eligible rarity set.
- Existing spawn/despawn timing and mythical/transcendant timing offsets.
- Existing no-candidate behavior: no presentation, message, despawn task, or duplicate chain.
- Existing catch success-before-optional-rewards ordering.
- Existing AFK catch and user-facing notification semantics unless failure recovery requires a documented change.
- Existing public method signatures and compatibility wrappers for `creature_picker`, `spawn_creature`, `get_spawn_bonus_effects`, `get_creature_rarity`, and `perform_mythical_check`.

### 4.2 Non-goals

This specification does not authorize:

- unrestricted `asyncio.gather` against the shared mutable database handler;
- arbitrary `asyncio.to_thread` calls without serialized ownership;
- a new public shutdown API;
- a silent duplicate-spawn cap;
- a change to active-bonus freshness;
- a redesign of unrelated inventory or cache systems;
- moving Discord UI object creation or mutation to a worker thread;
- retrying the complete catch callback as one opaque operation;
- changing gameplay probabilities to simplify implementation.

## 5. Target Architecture

```text
DiscordBot
  └── CreatureSpawnerHandler (lifecycle coordinator)
        ├── SpawnerLifecycleState
        ├── SpawnDecisionResolver
        │     ├── SpawnBonusContext
        │     └── SpawnCandidate
        ├── SpawnPresentationBoundary
        ├── DuplicatePolicy
        ├── AfkCatchBoundary
        └── EnvironmentScheduler

CreatureEncounterView
  ├── InteractionGate
  ├── CatchCommitService
  ├── ImmediateResponseBoundary
  └── PostCatchRewardCoordinator
        ├── AvatarRewardStage
        ├── ItemRewardStage
        └── Notification/Outbox Boundary

CreatureCaughtView
  ├── Event-loop UI state
  ├── Serialized profile/display state loader
  ├── Serialized favorite/nickname/release operations
  └── Prompt acknowledgement boundary
```

The target does not require every box to become a new public class. Private helpers or narrowly scoped internal collaborators are acceptable if their contracts are explicit and independently testable.

## 6. Phase 1 — Complete Spawner Separation and Task Observability

### 6.1 Lifecycle ownership

Retain `CreatureSpawnerHandler` as the lifecycle coordinator, but define explicit ownership for:

- `_spawner_task`
- `_environment_scheduler_task`
- `_environment_change_task`
- `_despawn_tasks`
- AFK notification tasks created by despawn handling

Extend task registration/completion behavior so every handler-owned task:

1. Is added to the correct ownership set or handle.
2. Has a completion callback.
3. Is removed from ownership when complete.
4. Calls `task.exception()` for non-cancelled tasks.
5. Logs non-cancellation failures with task type and correlation fields.
6. Does not treat normal cancellation as an operational error.
7. Is cancelled and awaited by `_cleanup_tasks` where ownership requires it.

The completion callback must not raise while inspecting a failed task.

### 6.2 AFK notification task policy

Choose and document one policy:

- **Tracked policy:** add AFK notification tasks to a private handler-owned task set and cancel/await them during cleanup; or
- **Best-effort policy:** attach a completion callback that consumes and logs exceptions, while explicitly documenting that shutdown does not guarantee delivery.

The default recommendation is the tracked policy because AFK notifications are user-visible. This must not block the event loop while waiting for database/image work.

### 6.3 Internal responsibility boundaries

Create or preserve these narrow boundaries:

| Boundary | Required responsibility |
|---|---|
| Lifecycle | Start claim, task handles, cleanup, completion, failure logging. |
| Bonus resolution | Resolve immutable active-bonus inputs without I/O or presentation. |
| Selection | Filter, fallback, copy, rarity/timing preparation, and no-candidate result. |
| Presentation | Generate embeds/views and send Discord messages after a valid candidate exists. |
| Duplicate policy | Decide initial/continuation duplicate behavior without changing probabilities. |
| AFK catch | Select trap user, perform durable AFK catch/reward work, schedule user-visible notification. |
| Environment | Decide, schedule, apply, announce, and wake the spawn loop. |

Do not extract classes merely to move lines. Each boundary must have a small input/output contract and a test that does not require a live Discord connection.

## 7. Phase 2 — Finish Active-Bonus and Selection Contracts

### 7.1 Complete `SpawnBonusContext`

The context must contain or expose:

- selected kingdom;
- requested/effective rarity;
- normal-charm interval state;
- mythical-charm identity or odds input;
- immutable source bonus identifiers;
- compatibility metadata needed to preserve user-truthiness mythical behavior.

The context must be created once per main-loop spawn attempt and passed through the internal decision path. Public compatibility wrappers may continue returning their existing tuples/values.

The resolver must:

- perform no database, image, Discord, or task operations;
- preserve random-call order where it affects gameplay;
- preserve current precedence behavior;
- provide deterministic unit-test seams;
- avoid treating a `TGOPlayer` object as a specific bonus identity.

If explicit bonus precedence is desired, record it as a separate product decision before changing current iteration-order behavior.

### 7.2 Complete `SpawnCandidate`

The internal candidate contract must contain:

- prepared creature;
- requested and effective rarity;
- mythical/transcendant state;
- spawn/despawn timing metadata;
- bonus context or the relevant immutable decision inputs;
- no Discord message, file, view, coroutine, or mutable database object.

The public `creature_picker` may continue returning `TGOCreature | None`, but the internal presentation path must consume the prepared candidate or an equivalent validated result. The candidate must be created before Discord presentation and discarded safely when no candidate exists.

### 7.3 Selection correctness

The selection boundary must test and preserve:

- kingdom filtering;
- rarity fallback order;
- empty kingdom behavior;
- empty rarity behavior;
- deep-copy isolation;
- mythical/transcendant timing;
- supplied-creature handling;
- no Discord I/O during selection;
- no mutation of the shared spawn pool.

## 8. Phase 3 — Make `CreatureCaughtView` Fully Responsive

### 8.1 Event-loop rule

Discord interaction acknowledgement and all Discord UI mutation remain on the event-loop thread. Database queries, writes, release calculations, profile reads, image/PIL generation, and other synchronous blocking work must run through `run_serialized_blocking` or a formally equivalent serialized boundary.

Do not construct a `discord.ui.View`, `Button`, `Select`, `Modal`, or `TextInput` in the worker. The worker returns plain data; the event-loop code constructs or mutates UI objects.

### 8.2 Constructor redesign

`CreatureCaughtView.__init__` currently performs synchronous profile/display reads. Replace that with one of these designs:

**Preferred design — preloaded state:**

1. Load the profile/display state through `run_serialized_blocking` before constructing the view.
2. Pass the plain loaded state into the constructor.
3. Construct the Discord view and components on the event-loop thread.

**Alternative design — lazy state loader:**

1. Construct a minimal view with no blocking reads.
2. Load state asynchronously before the first state-dependent interaction.
3. Keep an explicit loading/disabled state on the event loop.

The public constructor compatibility decision must be documented. Existing callers must not be broken without a migration wrapper.

### 8.3 Callback acknowledgement contract

Every caught-view callback must acknowledge before blocking work:

- buttons use `interaction.response.defer()` or an immediate response;
- modals acknowledge submission before database/image work;
- selects acknowledge before loading or writing state;
- callbacks use follow-up or edit-original-response after deferral;
- a callback never performs a synchronous database/PIL call before acknowledgement.

This applies to:

- analyze;
- favorite;
- display-creature selection;
- display-slot dropdown;
- nickname modal submission;
- release confirmation;
- storage expansion callbacks in `CreatureEncounterView`.

### 8.4 State mutation boundaries

For each action:

1. Validate user ownership and stale-view state on the event loop.
2. Acknowledge the interaction.
3. Execute database/image/release work through the serialized boundary.
4. Return plain results to the event loop.
5. Mutate view components on the event loop.
6. Edit the original response or send a follow-up.

The serialized worker must not mutate `View.children`, button objects, modal objects, or Discord messages.

### 8.5 Stale and concurrent view behavior

Define and test behavior for:

- original message deleted;
- caught creature already released;
- user no longer owns the catch;
- another component interaction is already updating the view;
- duplicate button clicks;
- nickname modal submitted twice;
- display-slot state changed by another command;
- Discord edit/send failure after durable database success.

The expected behavior is a prompt user-facing response, no duplicate durable mutation, and a logged classified failure when a Discord update cannot be completed.

## 9. Phase 4 — Idempotent Catch, Reward, and Release Processing

### 9.1 Required decision: idempotency mechanism

Before implementation, select and document one durable mechanism:

1. Existing database uniqueness constraints and conflict-safe writes;
2. A dedicated catch-reward ledger keyed by `(catch_id, reward_stage, reward_key)`;
3. A transactional outbox/idempotency table;
4. An equivalent existing mechanism proven by schema inspection and tests.

The preferred design is a durable reward-stage ledger if existing tables cannot express every reward category safely.

A catch ID alone is not automatically sufficient. The implementation must prove that each reward type has a stable deduplication key.

### 9.2 Catch commit

The catch commit must:

- have one durable catch identifier;
- enforce one successful catch for the applicable creature/user operation;
- be safe if the caller retries after a timeout;
- return the existing catch result when the operation was already committed;
- never duplicate XP or creature storage;
- preserve the synchronous `catch_creature` compatibility wrapper and async adapter.

Database uniqueness or conflict handling must be explicit. Catch insertion and XP update must have a documented transaction boundary.

### 9.3 Reward-stage keys

Define stable keys for every durable reward stage, for example:

```text
(catch_id, "event_avatar", avatar_id)
(catch_id, "quest_avatar", avatar_id)
(catch_id, "special_quest_avatar", avatar_id)
(catch_id, "milestone_item", milestone_id, item_id)
(catch_id, "random_item", reward_roll_id, item_id)
(catch_id, "afk_trap_charge", trap_link_id)
(catch_id, "release_reward", release_operation_id)
```

The actual keys must match the database model. Random rewards require a persisted roll/result or equivalent stable operation ID; generating a new random result during a retry is not idempotent.

### 9.4 Reward state machine

Each optional reward stage must have durable or otherwise recoverable state:

```text
PENDING -> CLAIMED -> NOTIFIED
PENDING -> FAILED_RETRYABLE
FAILED_RETRYABLE -> CLAIMED
CLAIMED -> NOTIFIED
```

Rules:

- A durable grant is written before its notification is sent.
- A notification failure must not roll back a successful grant.
- A retry checks the stage key before granting again.
- `CLAIMED` without `NOTIFIED` is safe to notify again without re-granting.
- Permanent failures are logged with a recovery identifier.
- The reward coordinator remains serialized unless database ownership is redesigned.

### 9.5 Reward coordinator and retries

Preserve the accepted eventual-reward behavior:

- final catch success response first;
- optional reward stages afterward;
- no unrestricted concurrent access to the shared database handler;
- narrow retries only around safe operations;
- no whole-callback retry.

The coordinator must tolerate:

- duplicate background task creation;
- process restart between grant and notification;
- Discord send failure;
- database timeout after commit;
- repeated callback invocation;
- partial completion of earlier reward stages.

### 9.6 Release and caught-view writes

Favorite, nickname, display-slot, release, and release-reward operations must have stable operation keys or conflict-safe update conditions. A repeated release callback must not release or pay the same creature twice.

Use ownership/state predicates where appropriate:

```text
UPDATE ...
SET released = true
WHERE catch_id = ? AND user_id = ? AND released = false
```

The result must distinguish:

- operation applied now;
- operation was already applied;
- user does not own the creature;
- creature is already released;
- retryable database failure.

## 10. Phase 5 — AFK and Environment Blocking Isolation

### 10.1 AFK catch path

The AFK path currently performs synchronous trap selection, database updates, catch/image work, and notification scheduling from an async despawn task. Refactor it so:

1. The despawn task remains responsible for message fetch/delete ordering.
2. AFK durable work runs through the serialized blocking boundary.
3. The result returns as plain data.
4. The Discord notification is scheduled/awaited according to the selected AFK task policy.
5. AFK failure does not prevent normal despawn completion or create an unobserved task exception.

Preserve trap charge semantics, AFK catch semantics, and notification content.

### 10.2 Environment image and announcement path

Environment advisory and landing-image generation are synchronous. Move image/file preparation behind the serialized blocking boundary while preserving:

- daily decision timing;
- pending-environment last-value behavior;
- persisted environment update order;
- spawn-pool reload order;
- announcement order;
- `spawn_event.set()` behavior.

Discord message sends remain on the event loop. Do not perform an event-loop `await` inside the blocking worker.

## 11. Phase 6 — Observability and Measurements

### 11.1 Structured logging

Replace `print`/traceback-only handling in the affected paths with the project logger or an equivalent structured logger. Each event should include only safe identifiers:

- stage;
- operation type;
- task type;
- creature ID when available;
- message ID when available;
- catch ID when available;
- user ID when appropriate;
- attempt number;
- elapsed milliseconds;
- failure class;
- retryable/permanent classification.

Never log tokens, credentials, full user objects, database connections, or image contents.

### 11.2 Stage timing

Add timing around:

- interaction acknowledgement;
- capacity check;
- catch commit;
- profile loading;
- embed/image preparation;
- public catch send;
- original spawn deletion;
- caught-view construction;
- each caught-view database/image operation;
- each avatar/item reward stage;
- AFK selection/charge/catch/notification;
- environment image preparation and announcement;
- despawn fetch/delete/notification;
- cleanup cancellation and task completion.

Use a monotonic clock. Make timing instrumentation low overhead and disable verbose per-operation logs through configuration if necessary.

### 11.3 Event-loop and reliability metrics

Measure:

- event-loop lag p50/p95/p99;
- interaction acknowledgement latency;
- critical catch latency;
- reward-stage completion latency;
- task failure count by task type;
- cancellation count during cleanup;
- idempotency conflict/replay count;
- reward stages stuck in `PENDING` or `CLAIMED`;
- Discord notification failure count.

Define alert thresholds before final A-level grading.

## 12. Testing Requirements

All tests must run without a live Discord connection. Database tests may use an isolated temporary database or deterministic handler fakes, but must exercise real uniqueness/transaction behavior before claiming idempotency.

### 12.1 Spawner and lifecycle tests

- completion callbacks consume task exceptions and log failures;
- cancellation is not logged as an operational failure;
- all owned tasks are cancelled/awaited by private cleanup;
- AFK notification ownership follows the selected policy;
- no thread, blocking sleep, or cross-thread `.result()` exists in remediated paths;
- bonus context, candidate, fallback, no-candidate, mythical, transcendant, and duplicate behavior remain compatible;
- environment task timing and `spawn_event` ordering remain unchanged.

### 12.2 Caught-view responsiveness tests

Use delayed blocking fakes and an event-loop heartbeat to prove:

- constructor profile/display loading is offloaded;
- analyze acknowledges before query completion;
- favorite acknowledges before update completion;
- display selection acknowledges before database completion;
- nickname modal acknowledges before persistence/image work completes;
- release confirmation acknowledges before release/reward calculation completes;
- storage expansion acknowledges before database payment/update work completes;
- one delayed caught-view callback does not delay another interaction.

### 12.3 Race and stale-state tests

- two users attempt the same catch;
- the same user invokes the catch twice;
- a catch callback is retried after an acknowledgement timeout;
- two reward workers process the same catch concurrently;
- favorite/nickname/display/release callbacks race;
- a stale view acts on an already released creature;
- the original Discord message is deleted before a component callback;
- a Discord edit fails after a database update;
- unauthorized users cannot mutate another user’s caught view.

### 12.4 Idempotency tests

For every reward category:

- first execution grants once;
- second execution returns already-applied without granting again;
- failure after durable grant can be retried safely;
- notification retry does not duplicate the grant;
- process-restart replay does not duplicate the grant;
- random reward replay returns the persisted result rather than rolling a new reward;
- release replay does not pay twice;
- AFK trap charge replay does not consume twice.

### 12.5 Measurement tests

- stage timers record expected names and durations;
- correlation identifiers propagate through catch/reward stages;
- no sensitive values are logged;
- event-loop lag measurement detects a controlled blocking delay;
- representative multi-encounter workload meets the A-level thresholds.

## 13. Rollout and Migration

### 13.1 Before schema changes

1. Inspect existing catch, user-creature, inventory, avatar-link, trap-link, and release tables.
2. Record existing uniqueness constraints and transaction behavior.
3. Select the idempotency mechanism.
4. Write a migration/backfill plan for any ledger or operation-key table.
5. Verify existing records will not violate new constraints.
6. Add rollback SQL or a reversible migration where possible.

### 13.2 Staged rollout

1. Deploy logging/timing first without changing behavior.
2. Deploy caught-view serialized boundaries behind a test/configuration gate.
3. Deploy idempotent catch/reward writes in shadow or test mode where possible.
4. Enable durable reward-stage state for a limited workload.
5. Compare latency, duplicate-conflict, task-failure, and reward-completion metrics.
6. Promote only after thresholds are met.
7. Remove compatibility branches only after replay and recovery tests pass.

### 13.3 Rollback

Rollback must be stage-specific:

- UI responsiveness rollback must not restore event-loop database/PIL work if the old path can freeze unrelated interactions; retain acknowledgement and worker boundaries.
- Reward rollback must preserve durable ledger records and prevent replay from granting duplicates.
- Schema rollback must not delete evidence of already-applied rewards.
- Task cleanup rollback must not restore untracked detached failures.
- Spawner decision rollback must not revert async despawn/environment/lifecycle remediation.

## 14. Acceptance Criteria

The implementation is complete only when:

- [ ] All owned asyncio tasks consume and classify exceptions.
- [ ] AFK notification tasks follow a documented ownership policy.
- [ ] Lifecycle, bonus, selection, presentation, duplicate, AFK, and environment boundaries have tests.
- [ ] `CreatureCaughtView` constructor and callbacks perform no blocking DB/PIL work on the event loop.
- [ ] Every caught-view callback acknowledges before blocking work.
- [ ] Stale, unauthorized, duplicate, and deleted-message interactions have defined behavior.
- [ ] Catch commits are idempotent under retry and replay.
- [ ] Every reward, release, favorite, nickname, display, and AFK charge write has a stable deduplication or state-transition rule.
- [ ] Durable grants occur before notifications.
- [ ] Notification retries do not duplicate grants.
- [ ] AFK and environment image/database work no longer blocks unrelated interactions.
- [ ] Structured stage timings and event-loop lag metrics are available.
- [ ] A-level latency and reliability thresholds are met in representative tests/runtime.
- [ ] Spawner and caught-view race/idempotency tests pass.
- [ ] Full test suite passes, or every unrelated failure is documented with owner and follow-up.
- [ ] `python -m py_compile` passes for all modified Python files.
- [ ] `git diff --check` passes.
- [ ] The final review document is updated with evidence, not assumptions.

## 15. Required Final Review Update

After implementation and validation, update `documentation/v2_5_5_specs/CREATURE_SPAWN_AND_ENCOUNTER_REVIEW.md`.

The update must:

1. Change the date and method from static-only to measured evidence when measurements exist.
2. Update the remediation table for every phase.
3. Regrade all areas based on actual test and runtime evidence.
4. Mark S1–S6 and E1–E5 resolved, partially resolved, or deferred with explicit reasons.
5. Record the final lifecycle/task ownership policy.
6. Record the selected idempotency mechanism and schema/migration status.
7. Record the caught-view acknowledgement and worker-boundary evidence.
8. Record AFK/environment isolation results.
9. Replace the open questions with final decisions or clearly owned deferred decisions.
10. Add exact test commands and results.
11. Add representative latency, event-loop lag, task-failure, and idempotency metrics.
12. Preserve the already-resolved compatibility decisions unless a separately approved product change supersedes them.
13. Do not claim an A grade for an area without tests and measurements supporting that grade.

## 16. Implementation Sequence

1. Baseline current latency, event-loop lag, task failures, and reward replay behavior.
2. Add structured logging and stage timing.
3. Complete task ownership, exception inspection, and AFK notification cleanup policy.
4. Complete caught-view state loading and callback serialized boundaries.
5. Add stale-view, ownership, and interaction race handling.
6. Inspect schema and choose the idempotency mechanism.
7. Implement catch commit idempotency.
8. Implement reward-stage ledger/state transitions and notification recovery.
9. Isolate AFK database/catch/image work.
10. Isolate environment image preparation.
11. Run focused unit, race, idempotency, and responsiveness tests.
12. Run representative multi-encounter latency tests.
13. Run the complete test suite and compile checks.
14. Review the final diff for compatibility regressions.
15. Update `CREATURE_SPAWN_AND_ENCOUNTER_REVIEW.md` with measured evidence and final grades.
16. Record any unresolved product decisions separately instead of silently changing behavior.


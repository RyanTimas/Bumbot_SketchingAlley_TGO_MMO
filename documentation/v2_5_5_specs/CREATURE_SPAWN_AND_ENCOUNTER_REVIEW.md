# Creature Spawning and Encounter Responsiveness Review

Date: 2026-10-23
Scope: `CreatureSpawnerHandler`, `CreatureEncounterView.catch_button_callback`, and directly called catch/unlock/reward paths.  
Method: Updated static review with source evidence, applied decision-pipeline remediation, and regression-test evidence. No production latency profile was available.

## 1. Executive Summary

`CreatureSpawnerHandler` now uses the intended asyncio concurrency model for scheduler ownership, creature despawn timers, and noon environment changes. The R1–R5 remediation is substantially implemented: sleeping OS threads and cross-thread `.result()` waits were removed, duplicate scheduler starts are claimed synchronously, and a private cleanup path cancels handler-owned tasks. The class still combines lifecycle orchestration, bonus interpretation, creature selection, spawn presentation, duplicate spawning, AFK capture, and environment scheduling, so separation-of-concerns concerns remain. Overall grade: **A- for the remediated timer/lifecycle model, C+ for structure, and C for spawn correctness/readability**.

The catch path is materially improved but not yet fully proven at A level. The critical catch, capacity checks, reward preparation, caught-view state preload, analyze flow, storage expansion, and caught-view database/image operations now use the serialized blocking boundary after acknowledgement. Discord UI construction and mutation remain on the event-loop thread. Schema-dependent catch/reward idempotency, production stage timing, and broader stale-view/race coverage are still required.

The decision-pipeline remediation is now applied incrementally: bonus resolution is represented by `SpawnBonusContext`, pool selection/preparation has private boundaries, `spawn_creature` safely skips empty selections, and duplicate probability decisions have explicit helpers. `CreatureSpawnerHandler` remains the lifecycle coordinator and still owns environment, AFK, presentation, and policy responsibilities, so this is a partial architectural improvement rather than a complete service extraction. The highest-value remaining work is durable catch/reward idempotency, AFK/environment blocking isolation, production measurement, and broader stale-view/race coverage. The caught-view blocking boundary and task-exception observability are now partially implemented.

### Remediation status

| Remediation item | Status | Current evidence |
|---|---|---|
| R1/R2 — despawn threads and blocking sleep | Implemented | `_despawn_creature` is an asyncio task using `await asyncio.sleep`; eligible despawns are tracked in `_despawn_tasks`. |
| R3 — noon environment scheduling | Implemented | `_schedule_environment_change` calculates the existing US/Eastern noon offset and awaits it on the bot loop. |
| R4 — cross-thread Discord submission and `.result()` | Implemented for the remediated paths | Fetch, delete, and despawn notification are awaited in order; AFK notification uses same-loop task creation. |
| R5 — duplicate scheduler start window | Implemented | `_spawner_start_claimed` is set before task creation and private `_cleanup_tasks` cancels owned tasks. |
| Catch critical path | Implemented with residual risk | `catch_creature_async`, capacity checks, reward preparation, and caught-view state preload use `run_serialized_blocking`; durable idempotency is not established. |
| Caught-view blocking boundary | Partially implemented | Analyze, storage, favorite, display, nickname, release, and release-image work is serialized after acknowledgement; compatibility constructor fallback and broader race tests remain. |
| Whole-callback retry removal | Implemented | The catch callback no longer retries the complete non-idempotent orchestration. |
| Quest-avatar batching | Implemented | Quest candidates are collected and batch-processed outside the per-avatar evaluation loop. |
| Decision-pipeline boundaries | Partially implemented | `SpawnBonusContext`, `SpawnCandidate`, pool-selection/preparation helpers, duplicate-policy helpers, and the no-candidate guard are implemented; the handler remains a broad coordinator. |
| No-candidate contract | Implemented | Empty pool/rarity selection returns `None`; `spawn_creature` performs no presentation, task registration, or duplicate spawning for `None`. |

## 2. Grades

| Area | Grade | Reason |
|---|---:|---|
| Spawner lifecycle/task ownership | A- | Synchronous start claim, task handles, tracked despawns, private cleanup, and failure consumption address the prior duplicate-start and sleeping-thread risks; production task metrics remain incomplete. |
| Spawner separation of concerns | B- | Private decision and duplicate-policy boundaries improve readability, but one class still owns lifecycle, environment, AFK, presentation, and selection responsibilities. |
| Active-bonus handling | B- | `SpawnBonusContext` centralizes kingdom/rarity activation, normal-charm interval state, source IDs, and first mythical-charm lookup while preserving one-time loading and iteration-order behavior; user truthiness remains a separate compatibility input. |
| Creature selection | B | Pool filtering, rarity fallback, deep-copying, timing preparation, and no-candidate handling are separated and tested; the public picker still returns a creature rather than a full candidate object for compatibility. |
| Despawn/environment coordination | A- | Despawn and environment waits no longer consume sleeping OS threads, and same-loop Discord operations preserve ordering; AFK/database/image work can still block the loop. |
| Catch callback responsiveness | B+ | Critical catch, caught-view preload, analyze, storage, favorite, display, nickname, release, and image preparation are serialized off-loop after acknowledgement; production thresholds and full callback race coverage remain unmeasured. |
| Catch concurrency isolation | B- | Blocking work is isolated and the per-view lock remains in place, but stale views, duplicate reward workers, ownership races, and durable state predicates still need explicit coverage. |
| Catch/reward reliability | B- | Whole-callback retry was removed and post-catch failures are logged, but reward writes/notifications remain independently partial and idempotency is not established. |
| Observability | C | Scheduler/despawn/AFK task failures are now consumed and logged, but stage timing, event-loop lag, reward replay, and production metrics are not yet available. |

## 3. Current Runtime Flow

### 3.1 Spawner flow

1. `DiscordBot.on_ready` calls `start_creature_spawner` (`src/discord/DiscordBot.py:88-101`).
2. `start_creature_spawner` synchronously claims lifecycle ownership before creating the spawn loop plus environment scheduler; repeated calls before the tasks yield are no-ops (`CreatureSpawnerHandler.py:88-107`).
3. `_creature_spawner` resolves one `SpawnBonusContext` per spawn attempt, calls `spawn_creature` with its public kingdom/rarity values, processes post-spawn events, and waits on the existing event/timeout (`CreatureSpawnerHandler.py:164-197`, `:328-360`).
4. `spawn_creature` selects or accepts a creature, applies the mythical check, builds/sends the encounter, schedules an asyncio despawn task for eligible rarities, and may recursively create swarm duplicates (`CreatureSpawnerHandler.py:202-219`, `:222-235`).
5. `creature_picker` delegates filtering/deep-copying to `_select_creature_from_pool` and rarity/timing mutation to `_prepare_spawn_candidate`, while preserving its creature-or-`None` public result (`CreatureSpawnerHandler.py:286-359`).
6. The handler also owns AFK trap capture, day/night changes, environment polling, and noon environment application. The environment transition is now an asyncio task and wakes the spawn loop through the existing `spawn_event` (`CreatureSpawnerHandler.py:396-471`).

### 3.2 Catch flow

`catch_button_callback` performs the following (`CreatureEncounterView.py:54-119`):

1. Defers the interaction and checks the per-view interaction lock (`:49-67`).
2. Performs the capacity check through `run_serialized_blocking` (`:70-75`).
3. Sends a short pending response, then calls `catch_creature_async`, which serializes the synchronous catch/profile/image/DB work off the event-loop thread (`:78-89`, `CatchFunctions.py`).
4. Sends the public catch message, preloads profile/display state through `run_serialized_blocking`, and constructs `CreatureCaughtView` with plain state on the event-loop thread (`:91-113`). The compatibility constructor fallback can still perform a synchronous profile lookup only when called without preloaded state.
5. Deletes the original spawn message and sends the final private success response before optional rewards (`:106-113`).
6. Runs avatar and item reward checks in a tracked background task after the critical response (`:115-119`, `:158-169`).

The main callback no longer performs the caught-view profile/display database reads inline. Component callbacks acknowledge first and move their database/image/release work through the serialized boundary; the remaining risks are idempotency, stale-state races, and unmeasured production latency.

## 4. CreatureSpawnerHandler Findings

### S1 — Lifecycle orchestration remains broad (B-; partially resolved)

**Evidence:** `CreatureSpawnerHandler.py:85-159`, `:164-197`, `:378-471`.

Private decision boundaries now separate bonus resolution, pool selection/preparation, and duplicate policy from the main presentation flow. However, `CreatureSpawnerHandler` still implements lifecycle, selection, presentation, AFK capture, day/night state, and environment transitions. The class is more readable, but it is not yet a thin coordinator and changes to environment or presentation can still interact with handler state.

**Current status:** The private-boundary portion is implemented; separate collaborators remain future work if the class continues to grow. Keep `CreatureSpawnerHandler` as the lifecycle coordinator and avoid splitting classes merely to move lines.

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

### S2 — Active bonuses are loaded once with centralized resolution (B-; partially resolved)

**Evidence:** `CreatureSpawnerHandler.py:45`, `:172-176`, `:263-298`, `:313-330`.

`active_bonuses` remains loaded once during initialization (`:45`). `_resolve_spawn_bonus_context` now centralizes kingdom/rarity activation, normal-charm state, source IDs, and first mythical-charm lookup. `get_spawn_bonus_effects` remains a compatibility wrapper, while `perform_mythical_check` uses the side-effect-free mythical-charm lookup and retains its separate user-truthiness input.

Specific readability/correctness concerns:

- `get_spawn_bonus_effects` overwrites `kingdom` and `rarity` as it iterates bonuses. If multiple bonuses are present, precedence is implicit in collection order rather than expressed as policy (`:318-330`).
- `perform_mythical_check` treats `user_bonus_active` as truthy rather than representing a specific user bonus decision (`:290-306`); `spawn_creature` passes the entire `user` object (`:206`).
- Charm effects, mythical odds, rarity fallback, and interval shortening are not all represented by one object passed through every public path; the context is used by the main spawn loop while public compatibility methods remain available.
- The one-time load is intentional according to the remediation decisions, but it means bonus changes after handler initialization are not reflected.

**Implemented design:** `_resolve_spawn_bonus_context` returns an immutable `SpawnBonusContext` once per main-loop spawn attempt containing:

- selected kingdom, if any;
- requested/preferred rarity, if any;
- mythical eligibility and odds modifier;
- interval modifier;
- source bonus IDs for diagnostics.

The context is used for main-loop kingdom/rarity inputs and interval selection. Active-bonus freshness remains unchanged; the improvement centralizes interpretation without silently refreshing state or changing precedence.

### S3 — Selection and spawning are partially separated (B; partially resolved)

**Evidence:** `CreatureSpawnerHandler.py:202-218`, `:263-298`.

`creature_picker` remains the public creature-or-`None` compatibility method, but it now delegates filtering/deep-copying to `_select_creature_from_pool` and rarity/timing preparation to `_prepare_spawn_candidate`. `spawn_creature` handles the no-candidate result before mythical checks, embed/view construction, Discord send, despawn registration, or duplicate spawning (`:202-235`, `:286-359`).

The decision work can now be tested without Discord I/O. A `SpawnCandidate` is an internal preparation result, while the public picker continues returning the creature to avoid changing existing callers.

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

**Status:** The no-candidate edge case is resolved. Empty kingdom or rarity selections return `None`; `spawn_creature` returns without constructing presentation objects, sending Discord output, registering despawn, or entering duplicate spawning. Regression coverage exists in `test_creature_spawner_handler.py`.

### S4 — Duplicate policy is explicit but recursion remains (C+; partially resolved)

**Evidence:** `CreatureSpawnerHandler.py:220-234`.

`_duplicate_creature_spawner` remains recursive, but initial and continuation decisions now use `_should_spawn_duplicate` and `_should_continue_duplicate_chain`. The existing 12%/6% behavior, eligible rarity set, chain multiplier, and user/bait exclusion remain unchanged. No gameplay-changing maximum chain cap was introduced.

**Remaining action:** If a maximum chain safety bound or duplicate diagnostics are desired, define them as a separate product decision. This remediation intentionally isolates policy without changing swarm probability or recursion semantics.

### S5 — Remaining synchronous work inside async paths (C)

**Evidence:** `CreatureSpawnerHandler.py:333-363`, `:421-471`.

The timer redesign removes thread-per-creature waits, and the interactive catch path now serializes its legacy database/PIL work. However, AFK handling still performs synchronous database reads/writes and synchronous catch/image work from the despawn task (`:346-358`). Environment transition still builds images synchronously before an awaited Discord send (`:442-463`). These operations can still block the event loop even though the timer itself is non-blocking.

**Recommendation:** Measure and isolate blocking DB/image work before moving it to threads. The existing shared query handler stores mutable `conn`/`cursor`, so an arbitrary `asyncio.to_thread` around concurrent database calls is not automatically safe. Use a serialized database worker/transaction boundary or refactor the query layer before broad offloading.

### S6 — Task completion and failure visibility are incomplete (C+)

**Evidence:** `CreatureSpawnerHandler.py:104-127`, `:130-159`, `:213-216`.

Task callbacks now remove completed scheduler and despawn task references, consume and log non-cancellation exceptions, and `_cleanup_tasks` cancels handler-owned scheduler/despawn/AFK notification tasks. Remaining work is to add production task-failure metrics and safe correlation identifiers to the structured logs.

**Status:** Task exception consumption and tracked AFK notification cleanup are implemented. Add production metrics and broader failure-injection coverage before awarding an A grade.

## 5. CreatureEncounterView Findings

### E1 — Blocking work remains in caught-view interactions (B+; partially resolved)

**Evidence:** `CreatureCaughtView.py`, `CreatureEncounterView.py`, `AsyncBlocking.py`.

The caught-view path now preloads profile/display state before UI construction and moves analyze, storage expansion, favorite, display, nickname, release, and release-image database/PIL work behind the serialized boundary after interaction acknowledgement. Discord `View` and component mutation remain on the event-loop thread.

**Remaining action:** Add focused tests for every callback, stale/unauthorized interactions, duplicate callbacks, and Discord failures after durable database success. The constructor’s compatibility fallback can still perform a synchronous profile lookup when called directly without preloaded state.

### E2 — The per-view interaction lock does not provide global responsiveness (D)

**Evidence:** `CreatureEncounterView.py:34`, `:52-67`.

The lock correctly serializes competing interactions for one creature and `self.caught` provides a second check (`:64-76`). The lock is released before the catch commit and reward chain begins, which avoids a long lock hold. It does not provide durable cross-view idempotency or protect against stale ownership state; a lock change alone is not a substitute for conflict-safe database transitions.

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

1. **Implemented:** Introduce an explicit immutable bonus decision/context used by interval and kingdom/rarity selection, with a side-effect-free mythical-charm lookup.
2. **Partially implemented:** Separate candidate selection/preparation from Discord presentation and task registration; the public picker remains a compatibility wrapper.
3. **Implemented:** Define and test the no-candidate contract for `creature_picker`/`spawn_creature`.
4. Add task exception logging and track detached AFK notification tasks in private cleanup.
5. Keep duplicate policy isolated without adding a gameplay-changing cap; add a cap or diagnostics only through a separate approved change.

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
- **RESOLVED:** No eligible creature is a normal skipped spawn: `creature_picker` returns `None`, and `spawn_creature` performs no presentation, Discord send, despawn registration, or duplicate spawning.

- **NEEDS REVIEW:** Can catch and reward writes be made idempotent using existing catch IDs/user-creature uniqueness rules?
- **ANSWER:** Yes, but it requires a separate product decision and careful review of all reward paths. The current implementation does not guarantee idempotency for all reward writes.

- **REQUIRES TRADEOFF:** Offloading synchronous database work to threads improves event-loop responsiveness but requires safe connection ownership; the current shared `QueryHandler` is not a safe arbitrary-concurrency boundary.
- **ANSWER:** Use a serialized database worker or transaction boundary to isolate synchronous work from the event loop. Arbitrary `asyncio.to_thread` calls are not safe with the current shared connection/cursor.

- **RESOLVED:** Multiple active kingdom/rarity bonuses preserve existing iteration-order overwrite behavior, including failed activation resets; changing precedence requires a separate product decision.
- **RESOLVED:** A private `_cleanup_tasks` path cancels handler-owned scheduler/despawn/AFK notification tasks on shutdown; completion callbacks consume and classify non-cancellation failures.

- **PARTIALLY RESOLVED:** Caught-view database and image work in the interactive catch path uses the same serialized boundary after prompt acknowledgement. The compatibility constructor fallback, stale-view/race tests, and production measurements remain required.

- **IMPLEMENTATION EVIDENCE:** `python -m unittest src.discord.tests.test_creature_spawner_handler src.discord.tests.test_catch_callback_responsiveness -v` — 17 focused tests passed, including task failure/cancellation/cleanup coverage and catch responsiveness coverage.
- **IMPLEMENTATION EVIDENCE:** `python -m py_compile src\\discord\\game_features\\creature_enounter\\CreatureSpawnerHandler.py src\\discord\\game_features\\creature_enounter\\CreatureCaughtView.py src\\discord\\game_features\\creature_enounter\\CreatureEncounterView.py src\\discord\\handlers\\CreatureReleaseService\\CreatureReleaseService.py src\\discord\\tests\\test_creature_spawner_handler.py` — passed.
- **DEFERRED:** Full catch/reward idempotency requires a durable operation/ reward-stage ledger or an approved schema migration. Existing `catch_id` is only an autoincrement key and random reward results are not persisted, so no idempotency claim is made here.
- **Residual limitation:** This review remains static with respect to production latency. The exact remaining split among SQLite, PIL, Discord, AFK handling, and caught-view/reward work requires stage timing in a representative runtime.


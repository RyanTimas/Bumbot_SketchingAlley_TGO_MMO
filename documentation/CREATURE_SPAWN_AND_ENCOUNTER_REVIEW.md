# Creature Spawning and Encounter Responsiveness Review

Date: 2026-10-22  
Scope: `CreatureSpawnerHandler`, `CreatureEncounterView.catch_button_callback`, and directly called catch/unlock/reward paths.  
Method: Static review with source evidence. No runtime profile or production trace was available.

## 1. Executive Summary

`CreatureSpawnerHandler` is functionally organized but currently combines lifecycle orchestration, bonus interpretation, creature selection, spawn presentation, duplicate spawning, despawn ownership, and environment scheduling in one class. Overall grade: **C+ for structure, B- for the implemented timer concurrency model, and C for spawn correctness/readability**. The most serious runtime issue is the catch callback: `CreatureEncounterView.catch_button_callback` performs synchronous database calls, synchronous image generation/conversion, and multiple sequential Discord/reward operations from an asyncio callback. Because synchronous work executes on the event-loop thread, one catch can prevent the bot from processing catch buttons on other spawned creatures. The reported approximately 15-second freeze is therefore plausible and should be treated as a **high-confidence event-loop starvation issue**, although exact time contribution must be measured by stage.

The highest-value remediation is to separate the catch transaction from post-catch unlock/reward presentation and move blocking database/image work behind a safe serialized database boundary or a properly isolated worker. For the spawner, introduce explicit bonus-resolution and creature-selection boundaries while retaining `CreatureSpawnerHandler` as the lifecycle coordinator.

## 2. Grades

| Area | Grade | Reason |
|---|---:|---|
| Spawner lifecycle/task ownership | B- | Duplicate-start protection, task tracking, and private cleanup exist; lifecycle state is still distributed across several task fields and callbacks. |
| Spawner separation of concerns | C+ | One class owns startup, scheduling, bonus policy, selection, presentation, duplicates, AFK capture, and environment changes. |
| Active-bonus handling | C | Bonuses are loaded once and interpreted in several methods with implicit precedence and mixed responsibilities. |
| Creature selection | C+ | Selection supports kingdom/rarity fallback, but selection, rarity mutation, and spawn-time calculation are coupled and `None` handling is unsafe. |
| Despawn/environment coordination | B- | Async timers avoid thread-per-creature overhead, but synchronous DB/image work remains in task paths and one-shot task ownership is complex. |
| Catch callback responsiveness | F | Blocking synchronous database/image work runs inside the event loop and is followed by a long serial chain of operations. |
| Catch concurrency isolation | D | The per-view lock protects one creature, but event-loop starvation affects every view; lock scope does not solve cross-view blocking. |
| Catch/reward reliability | C- | Multiple independent writes and notifications can partially complete; retrying the entire callback can repeat side effects. |
| Observability | D+ | No stage timing exists around catch DB, image, unlock, reward, and Discord operations; a generic execution timer cannot identify the bottleneck. |

## 3. Current Runtime Flow

### 3.1 Spawner flow

1. `DiscordBot.on_ready` calls `start_creature_spawner` (`src/discord/DiscordBot.py:88-101`).
2. `start_creature_spawner` claims lifecycle ownership and creates the spawn loop plus environment scheduler (`CreatureSpawnerHandler.py:85-101`).
3. `_creature_spawner` resolves bonus effects, calls `spawn_creature`, processes post-spawn events, and waits on the existing event/timeout (`CreatureSpawnerHandler.py:164-197`).
4. `spawn_creature` selects or accepts a creature, applies the mythical check, builds/sends the encounter, schedules despawn, and may recursively create swarm duplicates (`CreatureSpawnerHandler.py:202-218`, `:220-234`).
5. `creature_picker` filters the pool, applies rarity fallback, deep-copies the selection, changes mythical rarity when needed, and calculates despawn timing (`CreatureSpawnerHandler.py:263-298`).
6. The handler also owns AFK trap capture, day/night changes, environment polling, and noon environment application (`CreatureSpawnerHandler.py:333-471`).

### 3.2 Catch flow

`catch_button_callback` performs the following on the event loop (`CreatureEncounterView.py:45-99`):

1. Defers the interaction and checks the per-view interaction lock (`:49-67`).
2. Calls synchronous `catch_creature` (`:72`).
3. `catch_creature` performs a synchronous profile query, synchronous embed/image generation, catch insertion, and XP update (`CatchFunctions.py:10-20`).
4. Sends the public catch message (`CreatureEncounterView.py:75-77`).
5. Performs three avatar checks sequentially (`:82-85`).
6. Performs two item/reward checks sequentially (`:87-89`).
7. Deletes the original spawn message (`:91-95`).
8. Sends the final private success response (`:97-98`).

A single callback therefore mixes CPU/disk/image work, blocking SQLite access, network waits, and multiple dependent user notifications.

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

### S5 — Remaining synchronous work inside async paths (D+)

**Evidence:** `CreatureSpawnerHandler.py:333-363`, `:421-471`.

The timer redesign removes thread-per-creature waits, but AFK handling still performs synchronous database reads/writes and synchronous catch/image work from the despawn task (`:333-363`). Environment transition builds images synchronously before an awaited Discord send (`:421-471`). These operations can still block the event loop.

**Recommendation:** Measure and isolate blocking DB/image work before moving it to threads. The existing shared query handler stores mutable `conn`/`cursor`, so an arbitrary `asyncio.to_thread` around concurrent database calls is not automatically safe. Use a serialized database worker/transaction boundary or refactor the query layer before broad offloading.

### S6 — Task completion and failure visibility are incomplete (C)

**Evidence:** `CreatureSpawnerHandler.py:104-127`, `:130-159`, `:213-216`.

Task callbacks remove task references but do not inspect task exceptions. Detached AFK notification tasks created at `:361` are not added to `_despawn_tasks`, so shutdown cleanup does not wait for or cancel them. A failed detached notification can become an unobserved task exception.

**Recommendation:** Add a private task-registration helper that attaches a completion callback, removes the task from its set, and logs non-cancellation exceptions with creature/message identifiers. Track AFK notification tasks or intentionally define them as best-effort and log failures.

## 5. CreatureEncounterView Findings

### E1 — The catch callback blocks the entire event loop (F)

**Evidence:** `CreatureEncounterView.py:45-99`, `CatchFunctions.py:10-20`.

The callback is async syntactically, but several operations inside it are synchronous:

- `catch_creature` queries the user profile, generates the catch embed/image, inserts the catch, and updates XP synchronously (`CatchFunctions.py:12-20`).
- Avatar checks perform synchronous DB calls before each awaited notification (`AvatarUnlockHandler.py:23-30`, `:32-70`).
- Item reward checks perform synchronous DB reads/writes and image conversion (`ItemUnlockHandler.py:11-38`, `:43-55`).
- `convert_to_png` performs synchronous PIL encoding (`CommonFunctions.py:84-89`).
- The callback awaits multiple Discord sends serially (`CreatureEncounterView.py:70`, `:77`, `:83-89`, `:98`).

While this callback is executing synchronous sections, the asyncio event loop cannot dispatch catch buttons from other `CreatureEncounterView` instances. This directly explains why other creatures appear frozen even though each view has its own `asyncio.Lock`.

**Grade:** F for responsiveness, independent of whether the total wall time is exactly 15 seconds.

### E2 — The per-view interaction lock does not provide global responsiveness (D)

**Evidence:** `CreatureEncounterView.py:34`, `:52-67`.

The lock correctly serializes competing interactions for one creature and `self.caught` provides a second check (`:55-59`). However, the lock is released before the expensive catch/reward chain begins (`:56-67`, then `:69-98`). This is good for avoiding a long lock hold, but it does not prevent event-loop blocking from synchronous work. A lock change alone will not fix the reported freeze.

### E3 — Post-catch operations are fully serial (D+)

**Evidence:** `CreatureEncounterView.py:72-98`.

The callback waits for the catch transaction, public announcement, three avatar checks, two item checks, message deletion, and final response in sequence. Several of these checks are independent after the catch is durable, but blindly using `asyncio.gather` is unsafe while the functions contain blocking DB work and send user-visible messages. It can increase DB contention and reorder notifications.

**Recommendation:** Define phases:

1. **Critical catch phase:** validate ownership/capacity, persist catch and XP, and send the public catch announcement.
2. **Immediate user response:** send the final success response as soon as the critical phase succeeds.
3. **Post-catch rewards:** process avatar/item unlocks through a controlled background task or serialized worker, with idempotent writes and explicit notification policy.

Moving phase 3 after the final response is a **REQUIRES TRADEOFF** because it changes when unlock notifications appear. If exact current ordering is mandatory, keep phase 3 in the request but offload only safe blocking work and add stage timeouts/metrics.

### E4 — The retry decorator can repeat side effects (C-)

**Evidence:** `CreatureEncounterView.py:46-48`, `src/commons/CommonDecorators.py:18-35`.

`retry_on_ssl_error` wraps the entire catch callback. If a network SSL error occurs after the database catch insert, XP update, public announcement, or an unlock write, the wrapper can retry the whole callback. That can repeat side effects or produce inconsistent partial behavior. It also adds a one-second delay between attempts (`CommonDecorators.py:29-35`).

**Recommendation:** Apply retry boundaries only around the individual Discord operation that is safe to retry, or make catch/reward writes idempotent before retrying the orchestration. Never retry a non-idempotent catch transaction as one opaque callback.

### E5 — Quest unlock batching is incorrectly nested (D)

**Evidence:** `AvatarUnlockHandler.py:37-70`.

The code evaluates one quest avatar at a time (`:39-44`) but collects, checks, inserts, and notifies inside that same loop (`:46-70`). Consequences include repeated batch checks/inserts and an early `return` at `:56-57` before later unlockable avatars are evaluated. This is both a correctness problem and a latency amplifier.

**Recommendation:** Evaluate all unlock queries first, collect all eligible parent/child avatars once, perform one already-unlocked batch check, perform one batch insert, then send notifications. Add a regression test with multiple unlockable avatars.

## 6. Why the Callback Can Take 15 Seconds

The static evidence supports several additive contributors:

| Stage | Evidence | Likely cost |
|---|---|---|
| Catch profile + embed + image + DB writes | `CatchFunctions.py:12-20` | SQLite connection/query overhead, PIL rendering, disk/image work |
| Public catch send | `CreatureEncounterView.py:75-77` | Discord network/API latency |
| Event avatar checks | `AvatarUnlockHandler.py:23-30` | DB query plus one notification per unlock |
| Quest avatar checks | `AvatarUnlockHandler.py:32-70` | One query per avatar plus repeated batch work due nesting |
| Special quest check | `AvatarUnlockHandler.py:72-84` | Image conversion, notification, DB insert when triggered |
| Milestone reward | `ItemUnlockHandler.py:11-40` | Full user-creature count, multiple inventory reads/writes, up to three image notifications |
| Random reward | `ItemUnlockHandler.py:43-55` | Inventory reads/writes and image conversion when selected |
| Spawn deletion/final response | `CreatureEncounterView.py:91-98` | Discord API latency |
| Retry amplification | `CommonDecorators.py:18-35` | Additional one-second waits and repeated side effects after SSL failures |

The callback's total time is approximately the sum of these serial stages. More importantly, synchronous stages block unrelated interactions even while the callback is waiting for no explicit `await`.

**Required measurement:** Add stage timings around `catch_creature`, each unlock/reward function, message send/delete, image conversion, and database transaction boundaries. Record correlation fields such as user ID, creature ID, catch ID, and attempt number without logging sensitive tokens.

## 7. Prioritized Improvement Plan

### P0 — Restore event-loop responsiveness

1. Keep the initial interaction defer and per-view race protection.
2. Make the critical catch operation use a safe blocking-work boundary. Do not indiscriminately call `asyncio.to_thread` around the current shared `QueryHandler`; its mutable connection/cursor fields require serialized ownership or a redesigned transaction API.
3. Return/send the success response after the critical catch result instead of waiting for every optional unlock notification, **REQUIRES TRADEOFF** if notification ordering must remain exactly as today.
4. Move post-catch reward/unlock processing to a controlled task/worker with idempotent database writes and failure logging.

### P1 — Reduce catch work

1. Fix `check_for_quest_avatars` loop structure at `AvatarUnlockHandler.py:37-70`.
2. Replace the catch profile/insert/XP sequence at `CatchFunctions.py:12-20` with one transaction-oriented service where possible.
3. Batch profile/inventory/reward reads instead of issuing one connection per query; coordinate with the database remediation specification.
4. Avoid converting unlock images until a notification is actually going to be sent.
5. Use narrowly scoped Discord retries rather than retrying the entire callback.

### P2 — Improve spawner readability and correctness

1. Introduce an explicit immutable bonus decision/context used by interval selection, rarity selection, and mythical evaluation.
2. Separate candidate selection from Discord presentation and task registration.
3. Define and test the no-candidate contract for `creature_picker`/`spawn_creature`.
4. Add task exception logging and track detached AFK notification tasks.
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

- **NEEDS REVIEW:** Does the product require all avatar/item unlock notifications to appear before the final success response, or is eventual post-catch notification acceptable?
- **NEEDS REVIEW:** Can catch and reward writes be made idempotent using existing catch IDs/user-creature uniqueness rules?
- **REQUIRES TRADEOFF:** Offloading synchronous database work to threads improves event-loop responsiveness but requires safe connection ownership; the current shared `QueryHandler` is not a safe arbitrary-concurrency boundary.
- **NEEDS REVIEW:** Should the spawner treat no eligible creature as a normal skipped spawn or a logged operational error?
- **NEEDS REVIEW:** Should multiple active kingdom/rarity bonuses stack, choose highest priority, or use current iteration-order behavior?
- **NEEDS REVIEW:** Should detached AFK notifications be cancelled on shutdown or guaranteed to complete before shutdown?
- **Residual limitation:** This review is static. The exact 15-second split among SQLite, PIL, Discord, and unlock/reward work requires stage timing in a representative runtime.


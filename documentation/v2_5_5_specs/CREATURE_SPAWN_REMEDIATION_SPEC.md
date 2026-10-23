# Creature Spawn/Despawn Pipeline — Remediation Spec

## 1. Summary

Converge the Creature Spawn/Despawn Pipeline on the Discord bot's existing asyncio event loop: schedule despawn and noon environment-change delays as asyncio tasks, remove per-creature and environment-change OS threads, and perform Discord coroutine submission from the loop without blocking on `Future.result()`. Preserve the existing async spawn loop (`CreatureSpawnerHandler.py:93-123`), `spawn_event` wakeup (`CreatureSpawnerHandler.py:119-120`, `:388-389`), spawn/despawn wall-clock offsets, environment-change decision and announcement order, AFK-catch behavior, and public method contracts. No external dependency or new concurrency primitive is required; the design uses existing `asyncio.create_task` (`:84-85`) and `asyncio.sleep` (`:106`, `:331`, `:335`).

## 2. Risk Decision Records

### R1 — Thread-per-creature despawn timers

- **Evidence:** `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:140-143`
- **Risk restatement:** Each eligible spawned creature creates one daemon OS thread solely to wait for its despawn deadline.
- **Root cause:** `spawn_creature` constructs and starts `threading.Thread(target=self._despawn_creature, args=(creature, spawn_message))` for every non-Mythical/non-Transcendant creature (`:138-143`). The thread remains alive for the entire despawn delay.
- **Remediation:** Replace the thread construction/start block at `:140-143` with `asyncio.create_task(self._despawn_creature_async(creature, spawn_message))` on the already-running Discord event loop. Add the async implementation at the current `_despawn_creature` target (`:165-180`) or replace that private method in place; retain the existing arguments and all current despawn operations. The implementation must not create an executor or OS thread.
- **Timing equivalence:** The task must wait exactly `creature.time_to_despawn` seconds from task creation, matching `time.sleep(creature.time_to_despawn)` at `:167`. Task scheduling overhead may only be the event-loop scheduling overhead and must not intentionally adjust the delay.
- **State read/write and sharing:** Reads `creature`, `spawn_message`, `self.discord_bot`, `self.current_environment`, and shared `self.active_bonuses` indirectly through AFK handling. It may read/write shared `USER_CATCHES_*` and database-backed state through existing AFK logic. `self.current_environment` can be changed by environment logic (`:310-313`, `:369-375`); all access is same-event-loop after remediation. No spawn registry exists in the current class; do not introduce one solely for this fix. **THREADING RISK:** removed for this timer; external callers that mutate handler state from other threads remain outside this item.
- **Behavioral equivalence:** Preserve the rarity exclusion at `:139`, the delay, message existence check, deletion-before-AFK-catch order, `discord.NotFound` return behavior, despawn embed construction, and notification submission. The task is detached exactly as the current daemon thread is detached; task tracking/cancellation is specified under R5 only if lifecycle ownership is added without changing public behavior.
- **New primitives/dependencies:** Existing `asyncio.create_task` (`:84-85`) and existing async task execution only. **No approval required.** Do not add a dependency, executor, scheduler, or `loop.call_later`.
- **Tests:** No existing CreatureSpawnerHandler-specific tests were found; **NO EXISTING TESTS — CREATE**. Add tests that fake the event loop and message/channel, verify no `threading.Thread` is created, verify a despawn task waits for the exact delay, verify Mythical/Transcendant creatures do not schedule one, and verify the existing message/AFK/notification order.
- **Rollback:** Revert only the replacement at `:140-143` and the async private-method change at `:165-180`, restoring the daemon-thread call to `_despawn_creature` and its synchronous implementation. Leave R3/R4/R5 changes intact only if their code does not depend on the reverted method signature.
- **Expected grade after fix:** R1-specific risk becomes **A-/B+**: timer count is represented by event-loop tasks rather than one OS thread per creature; remaining cost is one task object per active despawn.

### R2 — Blocking `time.sleep` in despawn path

- **Evidence:** `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:167`
- **Risk restatement:** The despawn worker blocks an OS thread with `time.sleep`, and the same design cannot be used directly on the event loop.
- **Root cause:** `_despawn_creature` calls `time.sleep(creature.time_to_despawn)` before any Discord or AFK work (`:165-168`).
- **Remediation:** At `:165-167`, replace the synchronous private method with an async method whose first operation is `await asyncio.sleep(creature.time_to_despawn)`. The caller replacement is the R1 task creation at `:140-143`. Do not retain `time.sleep` in the new despawn path.
- **Timing equivalence:** `await asyncio.sleep(creature.time_to_despawn)` must use the unchanged value and must begin immediately when the replacement task is created. It therefore preserves the same nominal wall-clock offset as `time.sleep` while allowing other event-loop tasks to run.
- **State read/write and sharing:** The delay reads only `creature.time_to_despawn`; subsequent shared state is the same state listed for R1. `spawn_event` is not read or cleared by this change. **THREADING RISK:** none for the replacement delay when the task is created from the bot loop.
- **Behavioral equivalence:** The method remains detached from `spawn_creature`; the spawn coroutine still proceeds immediately after scheduling the despawn work. Only the waiting mechanism changes. Message fetch/delete, AFK catch, and despawn notification semantics remain governed by R4.
- **New primitives/dependencies:** Existing `asyncio.sleep` (`:106`, `:331`, `:335`). **No approval required.** `time.sleep` must not be used in the replacement path.
- **Tests:** **NO EXISTING TESTS — CREATE.** Use a controlled/virtual clock or mocked `asyncio.sleep` to assert the exact seconds argument, assert the event loop remains able to run another task during the wait, and assert cancellation does not execute post-delay despawn work.
- **Rollback:** Revert the async method and restore `time.sleep` at `:167`; then use the original thread caller from `:140-143`. This item can be reverted independently at the implementation level, subject to R1's thread-scaling regression.
- **Expected grade after fix:** R2-specific risk becomes **A**: no blocking sleep remains in the despawn path; the broader pipeline remains dependent on R1 and R4 being deployed consistently.

### R3 — Sleeping thread for environment-change scheduling

- **Evidence:** `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:353`, `:367`
- **Risk restatement:** A successful daily environment-change decision starts an OS thread that sleeps until noon.
- **Root cause:** `_handle_environment_change_cycle` starts `threading.Thread(target=self._schedule_environment_change, ..., daemon=True)` at `:352-353`; `_schedule_environment_change` blocks that thread with `time.sleep(time_until_environment_change)` at `:360-367`.
- **Remediation:** Replace the thread start at `:352-353` with `asyncio.create_task(self._schedule_environment_change())`. Replace `_schedule_environment_change` at `:360-389` with an async private coroutine whose delay operation is `await asyncio.sleep(time_until_environment_change)`. Keep the existing US/Eastern calculation at `:361-366`, pending-environment check and assignment at `:369-375`, announcement content at `:378-382`, pending reset at `:385-386`, and `self.spawn_event.set()` at `:388-389`.
- **Timing equivalence:** Compute `time_until_environment_change` using the same `US/Eastern` `current_time` and noon replacement at `:361-366`; await exactly that number of seconds. The environment application must occur at the same calculated noon offset, subject only to event-loop scheduling, and must not be changed to the hourly scheduler's next iteration.
- **State read/write and sharing:** Reads/writes `self.pending_environment` (`:350`, `:370`, `:386`), `self.current_environment` (`:371`, `:375`, `:380`), `self.creature_spawn_pool` indirectly through `define_environment_and_spawn_pool` (`:375`), persisted environment state (`:372`), and `self.spawn_event` (`:389`). It also writes the dynamically introduced `self.environment_changed_today` at `:354`; preserve that behavior unless separately reviewed. **THREADING RISK:** the current thread race is removed only if all handler access remains on the bot loop; direct external-thread mutation is out of scope and must not be added.
- **Behavioral equivalence:** Preserve the 11:00 eligibility and daily-check flow at `:316-335`, the 50/50 decision and non-current-environment selection at `:336-350`, noon application order, advisory send, pending reset, and event wakeup. The replacement must not alter whether a pending environment is applied if another operation changes or clears it before noon; that existing last-value behavior is retained.
- **New primitives/dependencies:** Existing `asyncio.create_task` (`:84-85`) and existing `asyncio.sleep` (`:331`, `:335`). **No approval required.** Do not add APScheduler, an executor, `loop.call_later`, or another timer dependency.
- **Tests:** **NO EXISTING TESTS — CREATE.** Test exact delay calculation around before-noon, noon, and after-noon inputs; verify no `threading.Thread` is started; verify pending environment persistence, pool reload, announcement, reset, and `spawn_event.set()` order; verify the hourly scheduler remains independent while spawning is disabled.
- **Rollback:** Revert only `:352-353` and `:360-389` to the original thread and synchronous sleep implementation. Preserve the daily decision logic at `:316-350`.
- **Expected grade after fix:** R3-specific risk becomes **A-/B+**: no sleeping OS thread is retained for an environment transition; residual event-loop task lifetime is bounded by the existing noon delay.

### R4 — Blocking `.result()` in the despawn path

- **Evidence:** `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:168-170`
- **Risk restatement:** The despawn worker synchronously waits for an event-loop coroutine, allowing a Discord/API stall to block the worker and propagate backpressure.
- **Root cause:** `_despawn_creature` submits `channel.fetch_message(...)` through `asyncio.run_coroutine_threadsafe` and immediately calls `.result()` at `:169-170`. Delete and notification operations are submitted from the worker at `:171` and `:179` without awaiting.
- **Remediation:** In the async despawn task created by R1, replace the fetch submission at `:169-170` with `await channel.fetch_message(spawn_message.id)`. Preserve the existing `discord.NotFound` handling at `:172-173`. Replace the delete and despawn-notification `run_coroutine_threadsafe` submissions at `:171` and `:179` with same-loop awaited calls, preserving fetch-before-delete, delete-before-AFK, and embed-before-notification ordering while making completion and errors observable. Preserve the existing synchronous `handle_afk_trap_catch` contract at `:270-281`; replace only its cross-thread AFK notification submission with an existing `asyncio.create_task` call on the current loop.
- **Timing equivalence:** The fetch still completes before the `discord.NotFound` branch and before AFK handling, as it does when `.result()` returns. Delete still occurs before AFK handling and notification still occurs after embed construction; awaiting these operations adds only their existing Discord API completion time and does not change the intentional timer offset or operation order.
- **State read/write and sharing:** Reads `spawn_message.channel.id`, `spawn_message.id`, `self.discord_bot.loop` no longer as a cross-thread submission target, and `self.current_environment` for embed construction. It writes no new shared state. **THREADING RISK:** the `.result()` worker wait is removed; all replacement coroutine operations must execute on the same bot loop as `spawn_creature`.
- **Behavioral equivalence:** Preserve fetch-before-delete validation, `discord.NotFound` early return, delete-before-AFK order, AFK result behavior, and post-AFK despawn-message order. The AFK helper remains synchronous and its database/catch behavior is unchanged; only its cross-thread notification submission changes to a same-loop task.
- **New primitives/dependencies:** Existing `asyncio.create_task` and normal `await` usage throughout the module. **No approval required.** `asyncio.run_coroutine_threadsafe` is removed from the despawn and environment-change paths, including the AFK notification previously at `:280` and the environment notification previously at `:378-382`.
- **Tests:** **NO EXISTING TESTS — CREATE.** Test a delayed/failing fetch without blocking an OS worker; test `discord.NotFound`; assert delete completes before AFK handling and notification completes after embed generation; test AFK notification task scheduling; assert no `.result()` or `run_coroutine_threadsafe` call remains in the despawn/environment implementation.
- **Rollback:** Revert only the async despawn message-operation changes at `:168-180` while retaining R1/R2 if desired; if reverted code requires a worker thread, rollback must restore the original R1 caller as well. Do not revert the environment-change path under R3.
- **Expected grade after fix:** R4-specific risk becomes **A**: no worker waits synchronously on the bot loop. Discord/network latency can still delay the event loop itself, which is an external operational risk rather than cross-thread blocking.

### R5 — Duplicate scheduler start window

- **Evidence:** `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:82-86`, `:94-97`
- **Risk restatement:** `start_creature_spawner` schedules two tasks before `_creature_spawner` executes and sets `_spawner_running`, leaving duplicate-start protection dependent on task scheduling order.
- **Root cause:** `start_creature_spawner` checks `_spawner_running` and immediately schedules both tasks at `:82-86`; `_creature_spawner` sets `_spawner_running = True` only after task execution begins at `:93-97`. The environment scheduler has no corresponding start guard.
- **Remediation:** At `:82-86`, add a synchronous start-claim state checked and set before either task is created, and store the two created task handles. The contract is: if the start claim is already active, return without creating either task; otherwise claim once, create exactly one spawn task and one environment-check task, then release the claim only when the owning lifecycle completes. At `:94-97`, retain `_spawner_running` as the running-state compatibility flag and ensure the spawn task's `finally` at `:123-124` clears both the running state and the start claim. The environment scheduler must use the same start ownership and must not independently create a second pair. Do not redesign the loop body or its `spawn_event` wait at `:99-123`.
- **Timing equivalence:** The first invocation still schedules the spawn and environment-check tasks immediately, with no added sleep or interval. Subsequent invocations that previously could race now become no-ops; this is the intended correction of duplicate scheduling, not a change to valid single-start behavior.
- **State read/write and sharing:** Touches `_spawner_running` (`:50`, `:94-97`, `:123-124`), the new start-claim flag, stored task handles, `are_creatures_spawning` (`:33`, `:89`, `:99`), and `spawn_event` indirectly through the unchanged loop and environment logic. **THREADING RISK:** the claim is safe only when `start_creature_spawner` is called on the bot event loop, as it is from the Discord ready lifecycle; if external threads call it, an event-loop dispatch policy is **NEEDS REVIEW**.
- **Behavioral equivalence:** Preserve the public `start_creature_spawner()` no-argument contract, the existing `_spawner_running` meaning, the independent environment-check loop, and all spawn-loop timing/event semantics. The only changed observable behavior is that repeated starts cannot duplicate schedulers.
- **New primitives/dependencies:** Existing asyncio task creation (`:84-85`) and task-handle state. **No approval required** for task handles or a boolean start claim; no lock, executor, scheduler library, or external dependency is introduced. If implementation chooses `Task.add_done_callback` for cleanup, that is an existing asyncio API but is not required by this specification; approval is **NOT REQUIRED** only if already supported by the project's Python version, otherwise mark **NEEDS REVIEW**.
- **Tests:** **NO EXISTING TESTS — CREATE.** Call `start_creature_spawner()` twice before yielding to the loop and assert exactly one spawn task and one environment task; assert `_spawner_running` cleanup on normal exit and cancellation; verify the existing `spawn_event` wakeup and 3–5 minute/1–3 minute interval behavior remain unchanged; verify environment checks continue when `are_creatures_spawning` is false.
- **Rollback:** Revert the start-claim and task-handle changes at `:82-97` and restore the original `_spawner_running` cleanup at `:123-124`. This restores the prior duplicate-start window without affecting R1-R4 timer implementations.
- **Expected grade after fix:** R5-specific risk becomes **A**: task ownership is claimed synchronously before scheduling, so repeated starts cannot create duplicate spawn/environment scheduler tasks.

## 3. Target Concurrency Model

| Concern | Target contract | Existing evidence preserved |
|---|---|---|
| Spawn loop | One asyncio task owns `_creature_spawner`; its loop body and waits are unchanged. | `CreatureSpawnerHandler.py:93-123` |
| Spawn wakeup | `spawn_event` remains the interruption mechanism; no replacement event or polling loop is introduced. | `:119-120`, `:388-389` |
| Creature despawn timers | One asyncio task per eligible despawn, with `await asyncio.sleep(time_to_despawn)`; zero OS threads per creature. | `:140-143`, `:165-167` |
| Environment transition timer | One asyncio task performs the existing computed noon delay; zero sleeping OS threads. | `:352-367` |
| Discord operations | Despawn task runs on the bot loop; fetch, delete, and despawn notification are awaited in their existing order, while the synchronous AFK helper schedules its notification on the same loop. | `:168-180`, `:270-281` |
| Lifecycle | Synchronous start claim owns exactly one spawn task and one environment-check task. | `:82-97` |
| Residual tradeoffs | Event-loop tasks still consume memory and can be delayed if synchronous database/image work blocks the loop. Moving those unrelated operations is outside R1-R5 and requires a separate specification. | `:176-180`, `:270-281`, `:357` |

This model is achievable for R1-R5 without an external dependency or a new scheduler. It does not claim that all runtime work is non-blocking: synchronous AFK/database/image operations remain outside this scoped remediation.

## 4. Shared-State Inventory

| Resource | file:line | Touched by | Risk |
|---|---|---|---|
| `_spawner_running` | `CreatureSpawnerHandler.py:50`, `:94-97`, `:123-124` | R5 | Duplicate ownership or stale running state if start claim and `finally` cleanup are not one lifecycle. **THREADING RISK** if public start is called outside the bot loop. |
| Start-claim flag and task handles (new handler state) | insertion at `CreatureSpawnerHandler.py:82-86` / initialization adjacent to `:49-50` | R5 | Must be claimed before task creation and cleared on completion/cancellation; no cross-thread mutation permitted without review. |
| `are_creatures_spawning` | `CreatureSpawnerHandler.py:33`, `:88-90`, `:99` | R5; unchanged loop | Toggle can stop the spawn loop while the independent environment scheduler continues. Preserve that distinction. |
| `spawn_event` | `CreatureSpawnerHandler.py:49`, `:119-120`, `:388-389` | R3, R5 tests; behavior otherwise unchanged | Clearing remains owned by the spawn loop; environment transition sets it. Do not add a second clear/set protocol. |
| `pending_environment` | `CreatureSpawnerHandler.py:40`, `:350`, `:370`, `:386` | R3 | Last-value replacement/clear semantics must remain. Same-loop execution removes the current environment-thread race. |
| `current_environment` | `CreatureSpawnerHandler.py:36`, `:71-77`, `:285`, `:312`, `:371-375` | R1/R3/R4 | Despawn embeds and environment transition can observe different valid environment values. Snapshotting or locking would alter semantics and is not part of this spec. **NEEDS REVIEW** if consistency is required. |
| `creature_spawn_pool` | `CreatureSpawnerHandler.py:42`, `:75-78`, `:186-214`, `:375` | R3; spawn reads unchanged | Pool replacement must occur in the existing `define_environment_and_spawn_pool` order. |
| `environment_changed_today` | `CreatureSpawnerHandler.py:354` | R3 | Attribute is created dynamically and is not initialized in `__init__`; preserve current behavior, but lifecycle/reset intent is **NEEDS REVIEW**. |
| `time_of_day`, `is_day`, `last_spawn_time` | `CreatureSpawnerHandler.py:43-45`, `:57-69`, `:284-313` | R1/R3/R4 read indirectly; no redesign | Same-loop ordering must not move day/night handling or alter spawn-time state updates. |
| `active_bonuses` | `CreatureSpawnerHandler.py:47`, `:113-117`, `:227-267` | R1/R4 indirectly; no redesign | Loaded once at initialization; freshness changes are outside scope and **NEEDS REVIEW**. |
| `USER_CATCHES_HOURLY`, `USER_CATCHES_DAILY` | `CreatureSpawnerHandler.py:293-300` | R1/R4 through AFK/catch path | Existing global mutable state; same-loop execution reduces pipeline thread races but does not redesign catch semantics. |
| Discord message/channel state | `CreatureSpawnerHandler.py:136`, `:168-180`, `:357`, `:378-382` | R1/R3/R4 | Preserve fetch validation, delete submission, AFK response, and announcement ordering; Discord API failures require existing exception policy. |

## 5. Remediation Ordering

1. **R5 first:** establish one owner for the spawn and environment-check tasks at `:82-97`; this prevents new timer tasks from being created by duplicate scheduler starts.
2. **R1 and R2 together:** replace the despawn thread and blocking sleep at `:140-143` and `:165-167` with one async despawn task. Do not deploy R2 alone while the caller still invokes a synchronous method from a thread.
3. **R4 immediately after R1/R2:** convert the despawn and AFK message operations at `:168-180` and `:270-281` to same-loop awaited operations only after the despawn method is an async task; preserve their existing order.
4. **R3:** convert environment scheduling at `:352-367` and its application path at `:369-389` to an async task. It may be implemented independently, but should follow R5 so lifecycle ownership and task cleanup are defined consistently.
5. **Parity validation:** run the new tests for single-start ownership, exact timer offsets, event wakeups, environment application, message ordering, AFK behavior, and cancellation before removing any rollback branch or legacy implementation.

## 6. Open Questions / NEEDS REVIEW

- **NEEDS REVIEW — lifecycle shutdown contract:** `CreatureSpawnerHandler.py` exposes `toggle_creature_spawner` but no shutdown method for the environment scheduler or detached despawn tasks. Decide whether task cancellation is intentionally omitted to preserve current daemon-thread lifetime, or whether a new private cleanup path is approved. Do not add a public method without an API decision.
- **ANSWER** -  we will not add a public method for shutdown, but we will add a private cleanup path to cancel tasks on bot shutdown.


- **NEEDS REVIEW — external callers:** `DiscordBot.py:70` constructs the handler and the ready flow starts it; grep found no other `CreatureSpawnerHandler` instantiation. Confirm that `start_creature_spawner` is never called from a non-bot thread before relying on same-loop start-claim state.
- **ANSWER** - This is correct, `start_creature_spawner` is only called from the bot ready flow and not from any other thread.


- **NEEDS REVIEW — environment consistency:** A despawn embed may read `current_environment` after a noon transition rather than the environment at spawn time; changing to a spawn-time snapshot would alter observable output. Keep current behavior unless product approval selects that tradeoff.
- **ANSWER** - We will keep the current behavior of reading `current_environment` at despawn time, as changing to a spawn-time snapshot would alter observable output and is not approved.


- **NEEDS REVIEW — pending environment replacement:** If multiple environment-change tasks can exist because of legacy state or restart behavior, define whether the newest `pending_environment` wins. The proposed single-start guard prevents normal duplicate scheduler creation but does not rewrite existing state.
- **ANSWER** - The newest `pending_environment` will win, as the proposed single-start guard prevents normal duplicate scheduler creation but does not rewrite existing state. This behavior is acceptable and does not require changes to the current implementation.


- **NEEDS REVIEW — `spawn_event` timing:** Preserve the existing set/clear ownership. A separate task must not clear the event, and no atomic event primitive should be introduced without approval.
- **ANSWER** - The existing set/clear ownership of `spawn_event` will be preserved. A separate task will not clear the event, and no atomic event primitive will be introduced without approval.


- **NEEDS REVIEW — active bonus freshness:** `active_bonuses` is initialized once at `:47`; refreshing it as part of this remediation would change spawn selection behavior and is excluded.
- **ANSWER** - We will not refresh `active_bonuses` as part of this remediation, as it would change spawn selection behavior and is excluded from the current scope.


- **RESOLVED — Discord operation completion:** Delete and despawn notification are awaited on the bot event loop as approved. The synchronous AFK helper remains contract-compatible and schedules its notification on the same loop without cross-thread submission. Tests cover the approved behavior.


- **NO EXISTING TESTS — CREATE:** No CreatureSpawnerHandler-specific test file was found. Existing `src/discord/tests/ShopTests.py` is unrelated and is not a substitute for pipeline regression coverage.
- **ANSWER** - We will create a new test file specifically for CreatureSpawnerHandler to cover the pipeline regression and ensure that all the changes made in this remediation are properly tested.

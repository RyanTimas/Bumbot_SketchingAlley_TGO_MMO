# Creature Spawner Decision Pipeline — Remediation Specification

**Status:** implementation applied incrementally; focused spawner tests pass. Full architectural extraction remains intentionally partial, with remaining boundaries and risks recorded in `CREATURE_SPAWN_AND_ENCOUNTER_REVIEW.md`.

## 1. Summary

Refactor `CreatureSpawnerHandler` so lifecycle orchestration, active-bonus interpretation, creature selection, spawn presentation, and duplicate policy have explicit internal boundaries. The implementation must preserve current gameplay behavior, public method contracts, spawn probabilities, active-bonus freshness, Discord message ordering, and the async lifecycle remediation already specified in `CREATURE_SPAWN_REMEDIATION_SPEC.md`.

This specification addresses the following findings from `CREATURE_SPAWN_AND_ENCOUNTER_REVIEW.md`:

- **S1 — Lifecycle orchestration is too broad**
- **S2 — Active bonuses are loaded once and interpreted in multiple places**
- **S3 — Selection and spawning are coupled**
- **S4 — Duplicate spawning is recursive and can multiply work**, limited to making the policy boundary explicit without silently changing probability

The target is an incremental decision pipeline, not a rewrite of the spawner or a new scheduling framework:

```text
CreatureSpawnerHandler
  ├── lifecycle coordination and task ownership
  ├── SpawnBonusContext resolution
  ├── SpawnCandidate preparation
  ├── spawn presentation
  ├── duplicate/swarm policy
  ├── AFK capture coordination
  └── environment coordination
```

No external dependency, new thread, executor, scheduler, lock, or public API is required for this remediation.

## 2. Current Implementation and Evidence

Primary implementation:

- `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py`

Relevant current responsibilities:

| Responsibility | Current implementation |
|---|---|
| Lifecycle ownership | `start_creature_spawner`, `_creature_spawner`, `_scheduler_task_completed`, `_cleanup_tasks` |
| Spawn interval selection | `_creature_spawner`, direct inspection of `active_bonuses` |
| Kingdom/rarity bonus interpretation | `get_spawn_bonus_effects` |
| Base rarity selection | `get_creature_rarity` |
| Mythical conversion | `perform_mythical_check` |
| Candidate filtering/preparation | `creature_picker` |
| Discord presentation | `spawn_creature` |
| Despawn task registration | `spawn_creature` |
| Duplicate/swarm behavior | `_duplicate_creature_spawner` |
| AFK trap capture | `handle_afk_trap_catch` |
| Environment/day-night coordination | `handle_post_spawn_events`, `_environment_change_check_scheduler`, `_handle_environment_change_cycle`, `_schedule_environment_change` |

The current code has two correctness hazards that this specification must address:

1. `creature_picker` can return `None` when a requested kingdom has no eligible creatures, while `spawn_creature` immediately reads `creature.local_rarity`.
2. Bonus precedence is an incidental consequence of list iteration. A later applicable bonus overwrites an earlier value, and a failed activation can reset a previously selected value. This behavior is not currently documented as policy.

## 3. Goals and Non-Goals

### 3.1 Goals

1. Make the lifecycle coordinator readable by extracting decision boundaries without changing its public API.
2. Represent one spawn attempt's resolved bonus inputs in an immutable, inspectable context.
3. Make candidate filtering, fallback, copying, rarity mutation, and timing preparation independently testable.
4. Define a safe no-candidate contract that skips a spawn without dereferencing `None` or sending a malformed Discord encounter.
5. Preserve current active-bonus loading behavior: `active_bonuses` is loaded during handler initialization and is not refreshed by this remediation.
6. Preserve current bonus activation probabilities and iteration-order behavior unless a separate product decision explicitly changes them.
7. Preserve mythical/transcendant behavior, supplied-creature behavior, duplicate-chain probabilities, spawn/despawn timing, and Discord presentation order.
8. Add focused regression tests for each new boundary.
9. Update `CREATURE_SPAWN_AND_ENCOUNTER_REVIEW.md` after implementation with the actual status, evidence, test results, and remaining tradeoffs.

### 3.2 Non-goals

The implementation must not:

- redesign `QueryHandler` or database connection ownership;
- refresh `active_bonuses` during each spawn;
- change charm, rarity, mythical, or duplicate probabilities;
- introduce a new scheduler or concurrency primitive;
- change the public signatures or return shape of `start_creature_spawner`, `spawn_creature`, `creature_picker`, `get_spawn_bonus_effects`, `get_creature_rarity`, or `perform_mythical_check` without an explicit compatibility decision;
- alter the async task ownership, despawn, environment scheduling, or cleanup behavior already implemented under `CREATURE_SPAWN_REMEDIATION_SPEC.md`;
- add a duplicate-spawn cap silently; a cap requires product approval because it can change swarm gameplay;
- move Discord `View`, embed, or message construction into a worker thread;
- fix unrelated `CreatureCaughtView` responsiveness issues under this spec.

## 4. Compatibility Contract

The following behavior is locked for this remediation:

| Behavior | Required compatibility |
|---|---|
| Active-bonus freshness | Continue loading `self.active_bonuses` once in `__init__`; do not refresh it during a spawn. |
| Bonus precedence | Preserve current iteration-order semantics: later applicable bonuses may overwrite earlier values, including a failed activation resetting the value. Document this as compatibility behavior rather than treating it as an accidental improvement opportunity. |
| Charm interval | Preserve the existing normal-charm interval range and the existing `random.uniform` call semantics. |
| Rarity selection | Preserve transcendant odds, dawn/dusk behavior, and common fallback behavior. |
| Kingdom selection | Preserve kingdom filtering and rarity fallback ordering. |
| Candidate copy | Continue returning a deep copy for pool-selected creatures so the shared spawn pool is not mutated. |
| Mythical handling | Preserve the current mythical check, ultra-charm behavior, chain multiplier, and transcendant bypass. |
| Timing | Preserve `refresh_spawn_and_despawn_time` and the 720-minute offset for mythical/transcendant candidates. |
| Supplied creature | Preserve current caller behavior when `spawn_creature(creature=...)` receives a concrete creature. Do not silently reapply pool selection or discard caller mutations. |
| No candidate | `creature_picker` continues returning `None`; `spawn_creature` treats `None` as a skipped spawn and performs no embed generation, Discord send, despawn registration, or duplicate spawning. |
| Presentation order | Candidate preparation precedes embed/view construction; message send precedes despawn task registration and duplicate handling, as in the current flow. |
| Public contracts | Existing callers, including AFK and bait-related callers, continue to receive the current creature-or-`None` result from `creature_picker` and the current `spawn_creature` awaitable behavior. |

## 5. Target Internal Contracts

### 5.1 `SpawnBonusContext`

Introduce an internal immutable value object. A frozen dataclass is preferred if the project’s existing Python version supports it; otherwise use an equivalent immutable named structure.

Suggested fields:

```text
SpawnBonusContext:
    kingdom: optional kingdom filter
    rarity: optional requested rarity
    normal_charm_active: bool
    mythical_bonus_item_id: optional item ID
    source_bonus_ids: immutable diagnostic tuple
```

The context may also include explicit interval and mythical-odds inputs if that makes the implementation clearer, but it must not duplicate mutable handler state unnecessarily.

Required properties:

- It is created from the existing `self.active_bonuses` snapshot.
- It records the result of the existing activation rolls for one spawn attempt.
- It does not reload game state.
- It does not perform Discord, database, image, or task operations.
- It makes precedence and activation behavior visible to tests and reviewers.

### 5.2 `SpawnCandidate`

Introduce an internal prepared-candidate value object or equivalent private contract. `creature_picker` may continue returning the public-compatible `TGOCreature | None`; the prepared structure is an internal boundary used between selection and presentation.

Suggested fields:

```text
SpawnCandidate:
    creature: TGOCreature
    requested_rarity: optional rarity/string
    selected_rarity: creature rarity/string
    was_mythical: bool
    despawn_delay: existing creature timing value
    bonus_context: SpawnBonusContext
```

The exact field set may be reduced if the existing creature object remains the source of truth, but the implementation must make these decisions inspectable without sending a Discord message.

Required properties:

- The candidate owns the deep-copied creature selected from the pool.
- It contains the final rarity/timing state used by presentation.
- It never contains a Discord message, view, file, or coroutine.
- It is safe to discard when no candidate is available.
- It does not mutate the shared `creature_spawn_pool`.

## 6. Implementation Plan

### Phase 1 — Establish private decision boundaries

Create the smallest set of private helpers or internal modules needed to isolate decisions. Prefer private methods first if that avoids unnecessary import cycles and preserves the handler’s current construction behavior.

Recommended boundaries:

| Boundary | Responsibility | Must not do |
|---|---|---|
| `_resolve_spawn_bonus_context` | Interpret the current `active_bonuses` snapshot and perform the existing activation rolls. | Send messages, query the database, refresh bonuses. |
| `_resolve_spawn_rarity` | Perform base rarity selection using existing time-of-day and transcendant rules. | Select a creature, mutate a candidate, or send Discord output. |
| `_select_creature_from_pool` | Filter by kingdom and rarity, preserve fallback ordering, choose an index, and deep-copy the selected creature. | Change rarity timing, generate embeds, or create tasks. |
| `_prepare_spawn_candidate` | Apply approved rarity mutation and spawn/despawn timing to the copied creature. | Send Discord output or register tasks. |
| `_present_spawn_candidate` or equivalent coordinator block | Generate embed/view and send the encounter. | Resolve bonus policy or perform pool filtering. |
| `_should_spawn_duplicate` / `_spawn_duplicate_chain` | Keep duplicate probability and chain multiplier behavior in one readable boundary. | Introduce an unapproved hard cap or alter probability. |

The final names may differ, but each responsibility must have one owner and focused tests.

### Phase 2 — Centralize active-bonus interpretation

Replace distributed bonus interpretation with one resolution path per spawn attempt.

The implementation must:

1. Read `self.active_bonuses` without refreshing it.
2. Preserve the existing kingdom and rarity activation rolls.
3. Preserve the current list-order overwrite semantics.
4. Preserve normal-charm detection for spawn interval selection.
5. Preserve mythical-charm selection and its existing first-match behavior.
6. Preserve the distinction between handler bonuses and the `user` truthiness passed into `perform_mythical_check`.
7. Make the resulting context available to selection and mythical evaluation.

The context must not accidentally make a user object equivalent to a specific bonus. If the existing `user_bonus_active` behavior is retained for compatibility, document and test that it remains a truthiness-based input until a separate gameplay decision changes it.

The `_creature_spawner` flow should read the context for interval behavior rather than independently scanning `self.active_bonuses`. If a supplied creature or duplicate path intentionally does not use all fields, preserve that behavior explicitly rather than applying the normal pool path indiscriminately.

### Phase 3 — Separate selection from presentation

Refactor `creature_picker` and `spawn_creature` in this order:

1. Resolve the requested kingdom/rarity inputs.
2. Filter the current spawn pool.
3. Return `None` when no eligible candidates exist.
4. Select using the existing random-index behavior.
5. Deep-copy the selected creature.
6. Apply the existing mythical rarity mutation and timing preparation.
7. Return the prepared creature or internal candidate.
8. In `spawn_creature`, handle the no-candidate result immediately.
9. Only after a valid candidate exists, perform mythical evaluation that currently belongs to presentation/coordinator flow.
10. Generate the embed and encounter view.
11. Send the Discord message.
12. Register the async despawn task for eligible rarities.
13. Apply existing duplicate behavior.

The implementation must explicitly decide whether mythical evaluation happens inside candidate preparation or immediately after selection in the coordinator. Either placement is acceptable only if:

- the current random-call order is preserved where it affects probabilities;
- transcendant creatures bypass mythical conversion;
- supplied creatures retain current behavior;
- mythical/transcendant timing remains correct; and
- tests cover the chosen order.

### Phase 4 — Make duplicate policy readable without changing it

Move duplicate probability and chain multiplier decisions behind a small private boundary. Preserve:

- the initial 12% duplicate behavior (`flip_coin(total_iterations=3)`);
- the eligible rarity set;
- the existing `critter_chain_multiplier` initialization;
- the mythical chain multiplier passed to `perform_mythical_check`;
- the subsequent duplicate probability (`flip_coin(total_iterations=1)`);
- the fact that user/bait spawns do not enter the swarm path.

Do not add a maximum chain count in this implementation unless product approval is recorded. If a safety cap is later approved, it must be a separate change with its own probability/gameplay tests.

### Phase 5 — Preserve lifecycle integration

The refactor must leave the async remediation intact:

- `start_creature_spawner` remains the synchronous start-claim boundary;
- `_creature_spawner` remains the owner of the spawn loop and `spawn_event` wait;
- despawn tasks continue to be created with `asyncio.create_task` and tracked in `_despawn_tasks`;
- environment scheduling remains on asyncio tasks with the existing noon calculation;
- `_cleanup_tasks` continues cancelling handler-owned tasks;
- no helper may create an OS thread or call `run_coroutine_threadsafe` for this decision pipeline.

## 7. No-Candidate Contract

This is a required correctness change, not an optional cleanup.

When a kingdom filter has no creatures, or when a rarity/kingdom combination has no fallback candidate:

1. `creature_picker` returns `None`.
2. `spawn_creature` returns without dereferencing the candidate.
3. No `CreatureEmbedHandler` is constructed.
4. No `CreatureEncounterView` is constructed.
5. No Discord message is sent.
6. No despawn task is created.
7. No duplicate chain is started.
8. The caller’s existing spawn loop continues to its post-spawn/event/cooldown behavior.

Add a debug-level or structured diagnostic if the project’s logging policy supports it, but do not turn a normal empty candidate pool into an exception or retry storm.

## 8. Testing Requirements

Create or extend `src/discord/tests/test_creature_spawner_handler.py`. Tests must not require a live Discord connection or production database. Use small fakes, `SimpleNamespace`, deterministic random patches, and isolated handler construction as the existing tests do.

### 8.1 Bonus-resolution tests

- Empty bonus snapshot produces the expected neutral context.
- Normal charm activates the existing shortened interval behavior.
- Kingdom charm activation preserves success/failure semantics.
- Rarity charm activation preserves success/failure semantics.
- Multiple applicable bonuses preserve current iteration-order overwrite behavior.
- A failed later activation preserves the current reset behavior if that is the existing implementation contract.
- Mythical charm selection preserves first-match behavior.
- Context creation does not reload active bonuses or game state.
- Context values are immutable or cannot be mutated through normal caller use.

### 8.2 Selection tests

- Kingdom filtering returns only creatures from the requested kingdom.
- Kingdom selection follows the existing rarity fallback ordering.
- No kingdom candidates return `None`.
- No eligible rarity candidates return `None` rather than raising.
- Pool-selected creatures are deep-copied and pool objects are unchanged.
- Requested mythical rarity applies mythical rarity and the 720-minute timing offset.
- Requested transcendant rarity preserves transcendant handling and timing.
- Ordinary candidates preserve existing timing behavior.
- Supplied creature behavior remains compatible with existing callers.
- Transcendant creatures bypass mythical conversion.
- Mythical evaluation preserves the existing odds inputs and chain multiplier.

### 8.3 Coordinator/presentation tests

- A valid candidate creates the embed/view and sends exactly one encounter message.
- The despawn task is created only after the encounter message succeeds.
- Mythical and transcendant candidates do not receive an ordinary despawn task.
- A `None` candidate sends no message, creates no view, and creates no task.
- Duplicate spawning is not entered for user/bait spawns.
- Duplicate probability and chain multiplier calls remain compatible with the current behavior.
- Candidate preparation does not perform Discord I/O.

### 8.4 Regression tests for lifecycle compatibility

- Existing start-claim and cleanup tests continue to pass.
- Existing despawn ordering tests continue to pass.
- Existing environment scheduler behavior remains unaffected.
- The decision refactor creates no `threading.Thread`, `time.sleep`, or `run_coroutine_threadsafe` call in the affected paths.

## 9. Observability Requirements

Add low-overhead diagnostic information only where the project’s current logging policy supports it. Do not log user-sensitive data or full mutable objects.

Recommended fields:

- spawn attempt identifier, if one already exists;
- requested kingdom and rarity;
- effective selected rarity;
- mythical/transcendant outcome;
- candidate availability result;
- duplicate chain multiplier;
- active bonus item IDs, if safe to log;
- elapsed decision time, if stage timing is already available.

At minimum, the implementation should make no-candidate skips distinguishable during tests and debugging without treating them as unhandled exceptions.

## 10. Rollback Plan

Rollback must be limited to this decision-pipeline remediation:

1. Restore the previous `get_spawn_bonus_effects`, `get_creature_rarity`, `perform_mythical_check`, and `creature_picker` bodies if the new boundaries produce a gameplay regression.
2. Restore the previous `spawn_creature` coordinator wiring while retaining the explicit `None` guard if it is independently safe and tested.
3. Restore the previous duplicate helper wiring without reverting the async despawn, environment scheduler, start-claim, or private cleanup work from `CREATURE_SPAWN_REMEDIATION_SPEC.md`.
4. Remove only new decision-context/candidate modules or private helpers that are no longer referenced.
5. Preserve the added regression tests, adjusting them to document the rollback state if necessary.

A rollback must not reintroduce thread-per-creature despawn timers, blocking environment sleeps, cross-thread `.result()` waits, or duplicate scheduler start races.

## 11. Acceptance Criteria

Implementation is complete when all of the following are true:

- [ ] Lifecycle, bonus resolution, selection, presentation, and duplicate policy have distinct private boundaries or narrowly scoped internal collaborators.
- [ ] `SpawnBonusContext` or an equivalent immutable context is used by the spawn decision path.
- [ ] Active bonuses remain one-time loaded and current activation probabilities/order are preserved.
- [ ] `SpawnCandidate` or an equivalent prepared-candidate contract separates selection from Discord presentation.
- [ ] No-candidate selection safely skips the spawn without dereferencing `None` or sending Discord output.
- [ ] Mythical, transcendant, supplied-creature, rarity-fallback, and timing behavior are covered by tests.
- [ ] Duplicate behavior remains probability-compatible and no unapproved cap is introduced.
- [ ] Existing async lifecycle remediation behavior remains intact.
- [ ] New and existing spawner tests pass without a live Discord connection.
- [ ] `git diff --check` passes.
- [ ] The final review update below is completed.

## 12. Required Final Documentation Update

After implementation and test validation, update:

`documentation/v2_5_5_specs/CREATURE_SPAWN_AND_ENCOUNTER_REVIEW.md`

The update is required in the same implementation change or immediately afterward and must:

1. Change the review date and implementation status.
2. Update the overall grades for:
   - spawner separation of concerns;
   - active-bonus handling;
   - creature selection;
   - spawn correctness/readability;
   - observability, if diagnostics were added.
3. Mark S1, S2, and S3 as resolved, partially resolved, or still open based on the actual implementation rather than the intended design.
4. Update S4 to distinguish an explicit duplicate-policy boundary from any future gameplay-changing cap.
5. Replace stale evidence and line references with the final symbols and source locations.
6. Record the no-candidate contract and its regression-test evidence.
7. Record compatibility decisions that were intentionally preserved, including:
   - one-time active-bonus loading;
   - iteration-order precedence;
   - rarity fallback order;
   - mythical/transcendant behavior;
   - supplied-creature behavior;
   - duplicate probabilities.
8. Add remaining risks or open questions instead of claiming full resolution where behavior is still coupled.
9. Record the exact test command and result.
10. Preserve the existing catch-flow findings unless separate implementation work changes them.

The review must not be updated merely because the spec exists. It must be updated only after implementation evidence and tests demonstrate which findings changed.

## 13. Implementation Sequence

1. Add the internal context/candidate contracts and focused unit tests.
2. Extract bonus resolution while preserving random-call and overwrite behavior.
3. Extract candidate filtering/preparation and add the no-candidate guard.
4. Wire the coordinator/presentation boundary without moving Discord UI construction off the event loop.
5. Isolate duplicate policy without changing probabilities.
6. Run the focused spawner tests, the full discovered test suite, and `git diff --check`.
7. Inspect the final diff for accidental changes to async lifecycle behavior and public method contracts.
8. Perform the required final update to `CREATURE_SPAWN_AND_ENCOUNTER_REVIEW.md`.
9. Re-run documentation validation and record any unrelated pre-existing test failures separately from implementation failures.


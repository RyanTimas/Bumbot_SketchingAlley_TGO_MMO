# PERFORMANCE_AUDIT

Date: 2026-10-22
Scope: `src/` runtime paths for Discord/TGOMMO (performance, concurrency, reliability under load)
Method: static deep read with evidence references (`file:line`)

## System Overview

- Language/runtime: Python, async Discord bot with `discord.py` and APScheduler (`requirements.txt:14`, `requirements.txt:4`, `src/discord/DiscordBot.py:50-53`).
- Process shape: startup initializes DB, cache registry, game state, then starts bot in a background thread (`src/Main.py:50-57`, `src/Main.py:60-65`).
- State model: SQLite DB via thin query wrapper + JSON file state (`src/database/handlers/QueryHandler.py:13-40`, `src/commons/GameStateManager.py:58-83`).
- Render model: many PIL image builds during command/view interactions (`src/discord/game_features/**/*ImageFactory.py`, e.g. `src/discord/game_features/encyclopedia/EncyclopediaImageFactory.py:77-113`).
- Caching: static-content cache registry with immutable snapshots and eager startup loading (`src/caching/cache_registry.py:74-89`, `src/caching/cache_startup.py:29-36`, `src/caching/db_specific_caches/creature_cache.py:45-51`).

## Grading Rubric

- `A`: no notable hot-path issues; scales safely for expected load.
- `B`: mostly healthy; some non-critical inefficiencies.
- `C`: mixed; moderate bottlenecks or race windows likely under growth.
- `D`: significant bottlenecks/concurrency hazards in common paths.
- `F`: critical correctness/perf risks likely to fail under normal load.

## Area Grades and Findings

### 1) Startup and Lifecycle Orchestration - **C+**

**What is working**
- Clear startup sequence and explicit cache warmup (`src/Main.py:50-57`, `src/Main.py:37-41`).
- Cache registry init is idempotent (`src/caching/cache_registry.py:68-73`, `src/caching/cache_registry.py:97-103`).

**Risks**
- Bot runs in a separate daemon thread but `main()` immediately `join()`s it, effectively blocking forever and complicating shutdown semantics (`src/Main.py:60-65`).
- Logging mostly done with `print` in async runtime paths, reducing observability and making latency hotspots hard to profile (`src/discord/DiscordBot.py:87-93`, `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:104-106`).

### 2) Database Access Layer (SQLite) - **D**

**What is working**
- Parameterized queries are used broadly, reducing SQL injection risk (`src/database/handlers/QueryHandler.py:32-35`).

**Risks**
- Every query opens/closes a new sqlite connection (`src/database/handlers/QueryHandler.py:13-15`, `src/database/handlers/QueryHandler.py:29-40`), increasing syscall/lock overhead on hot paths.
- No explicit busy timeout/WAL/journal tuning in connection setup (`src/database/handlers/QueryHandler.py:14-15`).
- Repeated read-modify-write patterns without transaction boundaries can lose updates under concurrency (currency/items): `update_user_profile_currency` and inventory updates call separate queries (`src/database/handlers/TGOMMO_DatabaseHandler.py:769-774`, `src/database/handlers/TGOMMO_DatabaseHandler.py:775-783`).
- Mutable default args in query-builder helpers can leak state across calls (`src/database/handlers/TGOMMO_DatabaseHandler.py:843`, `src/database/handlers/TGOMMO_DatabaseHandler.py:878`).

### 3) Static Cache Architecture - **B-**

**What is working**
- Snapshot-based caches use immutable tuples/mappings, good for read safety and low lock contention (`src/caching/db_specific_caches/creature_cache.py:45-51`, `src/caching/db_specific_caches/environment_cache.py:42-48`).
- Eager loading strategy is centralized (`src/caching/cache_startup.py:29-36`).

**Risks**
- `StaticItemCache` bypasses injected provider and hard-calls global DB handler in `_load_snapshot`, reducing testability and consistency (`src/caching/db_specific_caches/static_item_cache.py:30-33`).
- `reload_snapshot` prints to stdout for every cache reload (`src/caching/cache_base.py:84-89`) instead of structured logging.

### 4) Creature Spawn/Despawn Pipeline - **D+**

**What is working**
- Spawn loop itself is async and can be interrupted with event wakeup (`src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:93-123`, `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:389`).

**Risks**
- One OS thread per spawned creature for despawn timers (`src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:140-143`) + blocking `time.sleep` (`src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:167`) will scale poorly as spawn count rises.
- Environment-change scheduling also spins a sleeping thread with `time.sleep` (`src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:353`, `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:367`).
- `run_coroutine_threadsafe(...).result()` in despawn path can block worker threads and propagate loop stalls (`src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:170`).
- Potential duplicate scheduler start window: `start_creature_spawner` schedules tasks before `_spawner_running` is set in coroutine (`src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:82-86`, `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:94-97`).

### 5) Catch Interaction and Unlock Flow - **C-**

**What is working**
- Catch path serializes competing catches with an interaction lock (`src/discord/game_features/creature_enounter/CreatureEncounterView.py:34`, `src/discord/game_features/creature_enounter/CreatureEncounterView.py:56-59`).

**Risks**
- After catch, the callback performs a long serial chain of DB + messaging tasks in one request (`src/discord/game_features/creature_enounter/CreatureEncounterView.py:72-90`), likely increasing interaction latency.
- Quest avatar unlock batching currently runs per-loop due to indentation; checks/inserts are repeated and may return early before all avatars are evaluated (`src/discord/handlers/AvatarUnlockHandler/AvatarUnlockHandler.py:39-70`).
- `CreatureEmbedHandler.generate_afk_catch_embed` is infinitely recursive if called (`src/discord/game_features/creature_enounter/CreatureEmbedHandler.py:81-82`).

### 6) Inventory and Release Workflow - **D+**

**What is working**
- Release service offloads blocking DB work to executor thread (`src/discord/handlers/CreatureReleaseService/CreatureReleaseService.py:22-26`).

**Risks**
- Release DB operations are multiple independent writes with no transaction; partial updates are possible on failure (`src/discord/handlers/CreatureReleaseService/CreatureReleaseService.py:39-50`).
- Release operation returns failure when `currency_earned == 0` even if release succeeded (`if not currency_earned`) (`src/discord/game_features/creature_inventory/CreatureInventoryManagementView.py:107-109`).
- Storage expansion modal passes `user_id=self.message_author` object instead of `self.message_author.user_id`, causing wrong DB parameter and potential failures/retries (`src/discord/game_features/creature_inventory/CreatureInventoryView.py:133-134`).

### 7) Encyclopedia Rendering/Data Fetching - **D**

**What is working**
- Filtering options are rich and centralized in factory/view state (`src/discord/game_features/encyclopedia/EncyclopediaView.py:30-47`, `src/discord/game_features/encyclopedia/EncyclopediaImageFactory.py:43-60`).

**Risks**
- N+1 DB behavior in icon build: for each creature, at least two catch-stat queries plus optional first-variant query (`src/discord/game_features/encyclopedia/EncyclopediaImageFactory.py:125-127`, `src/discord/game_features/encyclopedia/EncyclopediaImageFactory.py:146-149`).
- Repeated image open/composition on each interaction (`src/discord/game_features/encyclopedia/EncyclopediaImageFactory.py:78-92`, `src/discord/game_features/encyclopedia/EncyclopediaImageFactory.py:155-170`) can become CPU/IO heavy under frequent page/filter toggles.

### 8) Shop / Trap / Item Interaction Paths - **C-**

**What is working**
- Shop restock is scheduled and isolated in its own service (`src/discord/handlers/ScheduledServices/ShopScheduler.py:26-57`).

**Risks**
- `@interaction_guard()` is used without binding a view instance in multiple callbacks, so guard checks/locking are effectively bypassed (`src/commons/CommonDecorators.py:49-54`, examples: `src/discord/game_features/shop/ShopView.py:32`, `src/discord/game_features/trap_manager/TrapManagerView.py:37`).
- Shop image build does per-item/per-avatar DB checks (sold out/owned) every render (N+1) (`src/discord/game_features/shop/ShopImageFactory.py:54-63`).
- Trap selection holds a global process lock while doing multiple DB reads and filtering, expanding lock contention (`src/discord/handlers/ItemUseHandler/TrapHandler.py:29-41`).

### 9) Game State Persistence (JSON) - **C-**

**What is working**
- Atomic file replace strategy is used for writes (`src/commons/GameStateManager.py:67-75`).

**Risks**
- Most getters/setters do load-modify-save without lock coverage, allowing races and lost updates under concurrent scheduler/view actions (`src/commons/GameStateManager.py:87-213`).
- Several loops assume keys exist and can crash if state is partially missing (e.g., iterating `state.get("current_shop_item_ids")` without default list) (`src/commons/GameStateManager.py:110-121`).

### 10) Object Construction and Media Loading - **D**

**What is working**
- Image fallback behavior is present for missing assets (`src/discord/objects/TGOCreature.py:91-104`, `src/discord/objects/TGOAvatar.py:68-76`, `src/discord/objects/TGOPlayerItem.py:45-49`).

**Risks**
- Core domain objects load/decode images in constructors; large query result sets multiply disk IO and memory pressure (`src/discord/objects/TGOCreature.py:83-105`, `src/discord/objects/TGOAvatar.py:57-80`, `src/discord/objects/TGOPlayerItem.py:38-51`).
- Player object construction issues extra DB lookups for six display slots (`src/discord/objects/TGOPlayer.py:44-53`), amplifying profile fetch cost.

### 11) Deprecated Surface (`zz_deprecated`) - **B-**

**What is working**
- Deprecated code appears isolated under `src/zz_deprecated` and not referenced by active runtime modules in current search.

**Risks**
- Large stale tree still carries dependencies and maintenance risk; only internal deprecated imports were observed (`src/zz_deprecated/twitch/TwitchBot.py:5`).

## Prioritized Action Checklist

1. [High Impact | Medium Effort] Replace per-spawn/per-change sleeping threads with async tasks and cancellable timers in `CreatureSpawnerHandler` (`src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:140-143`, `:167`, `:353`, `:367`).
2. [High Impact | Medium Effort] Rework `QueryHandler` connection strategy (pooled/reused connections per thread or async queue, plus WAL/busy_timeout) (`src/database/handlers/QueryHandler.py:13-40`).
3. [High Impact | Medium Effort] Add transactional boundaries for multi-step economy writes (release flow, purchases, trap charging) (`src/discord/handlers/CreatureReleaseService/CreatureReleaseService.py:39-50`, `src/database/handlers/TGOMMO_DatabaseHandler.py:769-783`, `src/discord/game_features/shop/ShopView.py:164-172`).
4. [High Impact | Low Effort] Fix mutable default args in query helper methods (`src/database/handlers/TGOMMO_DatabaseHandler.py:843`, `:878`).
5. [High Impact | Low Effort] Fix `AvatarUnlockHandler.check_for_quest_avatars` loop structure so batching/check/insert runs once after evaluating all avatars (`src/discord/handlers/AvatarUnlockHandler/AvatarUnlockHandler.py:39-70`).
6. [High Impact | Low Effort] Fix recursion bug in `generate_afk_catch_embed` (`src/discord/game_features/creature_enounter/CreatureEmbedHandler.py:81-82`).
7. [High Impact | Medium Effort] Remove N+1 query patterns in encyclopedia icon generation by precomputing catch stats in bulk (`src/discord/game_features/encyclopedia/EncyclopediaImageFactory.py:125-127`, `:146-149`).
8. [Medium Impact | Medium Effort] Decouple PIL asset loading from object constructors; introduce lazy/shared image asset cache (`src/discord/objects/TGOCreature.py:83-105`, `src/discord/objects/TGOAvatar.py:57-80`, `src/discord/objects/TGOPlayerItem.py:38-51`).
9. [Medium Impact | Low Effort] Correct storage expansion DB call to pass integer `user_id` (`src/discord/game_features/creature_inventory/CreatureInventoryView.py:133-134`).
10. [Medium Impact | Low Effort] Correct release success check to allow valid zero-currency outcomes (`src/discord/game_features/creature_inventory/CreatureInventoryManagementView.py:107-109`).
11. [Medium Impact | Low Effort] Ensure interaction guards are actually bound to view instances where concurrency/user checks matter (`src/commons/CommonDecorators.py:49-56`, `src/discord/game_features/shop/ShopView.py:32`, `src/discord/game_features/trap_manager/TrapManagerView.py:37`).
12. [Medium Impact | Medium Effort] Add lock coverage (or serialized writer queue) for all `GameStateManager` read-modify-write operations (`src/commons/GameStateManager.py:87-213`).
13. [Medium Impact | Low Effort] Move hot-path `print` diagnostics to structured logging with context and timings (`src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:104-106`, `src/discord/DiscordBot.py:87-93`).
14. [Medium Impact | Medium Effort] Reduce shop render DB chatter by snapshotting ownership/purchase status once per render (`src/discord/game_features/shop/ShopImageFactory.py:54-63`).
15. [Low Impact | Low Effort] Replace `cache_base.reload_snapshot` stdout print with logger call (`src/caching/cache_base.py:84-89`).
16. [Low Impact | Low Effort] Prune/archive `src/zz_deprecated` behind tooling exclusions and docs to prevent accidental drift (`src/zz_deprecated/*`).

## Residual Risks / Gaps

- This audit is static-only (no runtime profiling traces, no synthetic load test data).
- Discord gateway/network jitter and SQLite contention behavior should be validated with workload scripts after fixes.
- Current tests are command-driven/manual and do not provide regression/perf assertions (`src/discord/tests/*.py`).


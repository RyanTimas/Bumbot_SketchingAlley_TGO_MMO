# Performance Audit — Remediation Specifications

Date: 2026-10-22  
Source audit: `documentation/PERFORMANCE_AUDIT.md`  
Scope: Audit areas 1–3 and 5–11. Creature Spawn/Despawn Pipeline area 4 is specified separately in `documentation/CREATURE_SPAWN_REMEDIATION_SPEC.md`.

## 1. Portfolio Contract

These are implementation specifications, not source changes. Every remediation below preserves existing public method signatures and user-visible behavior unless explicitly marked **REQUIRES TRADEOFF**. Existing primitives are preferred: `asyncio`, `threading.RLock`, the existing executor path, SQLite, structured `logging`, and the existing cache registry. No external dependency is approved by this document. Any option that adds a pool, queue, scheduler, schema migration, or image library feature is marked **APPROVAL REQUIRED**.

Common implementation contract for every area:

- Preserve current success/error messages, ordering, retry behavior, and persisted values.
- Add regression tests before replacing a hot path; the audit found no dedicated performance regression suite.
- Roll back one area at a time using the area-specific file/function boundary below.
- Measure before/after latency, query count, image decode count, lock wait, and failure rate in runtime validation; static review alone cannot prove load behavior.

## 2. Area Decision Records

### A1 — Startup and lifecycle orchestration (current grade C+)

- **Evidence / root cause:** `src/Main.py:44-65` runs an async `main`, starts `initialize_discord_bot` in a daemon `threading.Thread` at `:60-62`, then blocks in `thread.join()` at `:64-65`. Runtime paths use `print`, including `src/discord/DiscordBot.py:85-93` and `src/discord/game_features/creature_enounter/CreatureSpawnerHandler.py:103-106`.
- **Remediation contract:** Keep initialization order at `Main.py:47-57`. Replace the daemon-thread/join boundary at `Main.py:59-65` with one explicitly owned bot-loop lifecycle, or retain the thread only if Discord library requirements prove it necessary; in either case, define shutdown ownership and avoid an unbounded join from the asyncio bootstrap. Replace runtime `print` calls at `DiscordBot.py:87-93` and `CreatureSpawnerHandler.py:104-106` with the module/class logger while preserving message severity and exception traceback.
- **Behavioral invariants:** directories, database, cache, game state, and bot initialization occur in the same order; bot startup is not duplicated; startup errors remain visible; shutdown does not terminate before bot cleanup.
- **Shared state / risk:** `threads` (`Main.py:45`, `:60-65`), global DB/cache/game-state singletons (`Main.py:51-57`), and the bot event loop. **THREADING RISK:** changing thread ownership can move Discord initialization across loop boundaries. **NEEDS REVIEW:** verify `DiscordBot.start_bot()` loop/thread requirements before selecting same-loop startup.
- **New primitives/dependencies:** existing `asyncio.run`, `threading.Thread`, and `logging`; no new dependency. A new shutdown signal or executor is **APPROVAL REQUIRED**.
- **Tests:** **NO EXISTING TESTS — CREATE.** Verify initialization order, `RUN_DISCORD_BOT=False`, startup exception logging, exactly one bot startup, and bounded shutdown under a fake bot.
- **Rollback / grade:** Revert only `Main.py:59-65` and logging call sites. Expected grade **B+/A-** after lifecycle ownership and structured logging are validated; residual grade depends on Discord's required loop model.

### A2 — SQLite database access layer (current grade D)

- **Evidence / root cause:** `src/database/handlers/QueryHandler.py:13-15` creates a fresh connection for every operation; `:29-40` executes/fetches/commits/closes each query. Multi-step economy updates are separate calls at `src/database/handlers/TGOMMO_DatabaseHandler.py:769-783`; mutable default query parameters are at `:843` and `:878`.
- **Remediation contract:** First add an explicit transaction-capable API in `QueryHandler.py` adjacent to `execute_query` (`:29-40`) that opens one connection for a caller-owned unit of work, commits on success, rolls back on failure, and always closes. Add SQLite connection settings at `:13-15` only after measuring: `timeout`/busy handling and WAL are operational decisions. Refactor currency/item/release/purchase/trap multi-step operations to use that unit at `TGOMMO_DatabaseHandler.py:769-783` and their call sites. Change `params=[]` to `params=None` at `:843` and `:878`, creating a local list before appending.
- **Behavioral invariants:** parameter binding remains intact; existing return values and query ordering remain unchanged; a failed multi-write leaves all writes from that unit unapplied; reads outside a unit retain current results.
- **Shared state / risk:** `QueryHandler.conn` and `.cursor` (`QueryHandler.py:9-10`) are mutable instance fields. **THREADING RISK:** the existing handler is shared globally (`DatabaseHandler.py`); a reused connection must not be shared concurrently across executor threads. A per-operation connection or explicitly serialized transaction is safer than an unapproved pool.
- **New primitives/dependencies:** existing `sqlite3` transactions and connection options; no dependency. A connection pool, async SQLite driver, or queue is **APPROVAL REQUIRED**.
- **Tests:** **NO EXISTING TESTS — CREATE.** Test rollback/commit, concurrent currency updates, inventory dummy-record behavior, query-builder parameter isolation, busy/locked behavior, and query-count/latency before versus after.
- **Rollback / grade:** Roll back the transaction API and call-site migration while retaining mutable-default fixes independently. Expected grade **B-/B** after transaction and contention validation; SQLite remains a single-file throughput boundary.

### A3 — Static cache architecture (current grade B-)

- **Evidence / root cause:** immutable snapshot construction exists in `src/caching/cache_base.py:84-89` and the static caches. `src/caching/db_specific_caches/static_item_cache.py:26-34` accepts `self._db_provider` at `:28` but `_load_snapshot` calls global `get_tgommo_db_handler()` directly at `:31`. Reload emits stdout at `cache_base.py:85`.
- **Remediation contract:** At `static_item_cache.py:30-34`, call the injected `self._db_provider()` and keep tuple/mapping-proxy snapshot construction unchanged. At `cache_base.py:84-89`, replace `print` with the cache's existing logger, preserving the reload event and timing decorator behavior. Do not change eager registration or snapshot publication semantics.
- **Behavioral invariants:** first-load behavior, cache contents, immutable read snapshots, and eager startup timing remain unchanged; provider injection becomes effective for tests and alternate DB instances.
- **Shared state / risk:** registry singleton and lock (`cache_registry.py:68-73`, `:97-103`), per-cache `_snapshot` and `_lock` (`cache_base.py:87-94`). **THREADING RISK:** retain lock-protected publication; never mutate a published snapshot.
- **New primitives/dependencies:** existing provider callback and logger; no dependency or primitive. A TTL/background reload scheduler is **APPROVAL REQUIRED** and out of scope.
- **Tests:** **NO EXISTING TESTS — CREATE.** Inject a fake provider, assert it is called, assert global DB is not called, verify snapshot atomicity during reload, and verify structured reload logging.
- **Rollback / grade:** Revert `static_item_cache.py:30-34` and `cache_base.py:84-89` independently. Expected grade **B+/A-**; remaining cache cost is intentional startup memory/eager-load work.

### A5 — Catch interaction and unlock flow (current grade C)

- **Evidence / root cause:** catch serialization uses `asyncio.Lock` at `src/discord/game_features/creature_enounter/CreatureEncounterView.py:34`, `:52-67`; successful catch then performs DB, Discord, avatar, item, deletion, and follow-up work serially at `:69-98`. Quest unlock evaluation and batching are incorrectly nested inside the avatar loop at `src/discord/handlers/AvatarUnlockHandler/AvatarUnlockHandler.py:37-70`. The audit also identifies recursive AFK embed behavior at `CreatureEmbedHandler.py:81-82`.
- **Remediation contract:** Preserve the interaction lock and double-check at `CreatureEncounterView.py:52-61`. Split the post-catch chain at `:72-98` only into explicitly ordered phases: durable catch first, required public channel announcement second, unlock/reward processing third, original-message deletion and final follow-up last. Do not parallelize user-visible sends without approval. In `check_for_quest_avatars`, move collection/check/insert/notification blocks (`AvatarUnlockHandler.py:46-70`) after the complete `for avatar` evaluation (`:39-44`), so all unlock conditions are evaluated once. Replace the recursive call at `CreatureEmbedHandler.py:81-82` with the intended non-recursive embed builder after confirming the target helper. **NEEDS REVIEW:** exact intended AFK text/helper is not derivable from the audit alone.
- **Behavioral invariants:** one catch wins; catch database state precedes unlock processing; each new avatar notification is sent once; final success response remains after processing; no unlock is granted for a failed condition.
- **Shared state / risk:** `self.caught`, `interaction_lock`, catch DB rows, avatar/item links, and Discord messages. **THREADING RISK:** blocking DB calls inside async callbacks remain unless the database remediation A2 is deployed; moving them to an executor changes transaction ownership and requires coordination.
- **New primitives/dependencies:** existing `asyncio.Lock` and current async calls; no dependency. Background task fan-out is **APPROVAL REQUIRED** because it changes completion/error ordering.
- **Tests:** **NO EXISTING TESTS — CREATE.** Concurrent catch race, failed/full inventory, all-avatar batch evaluation, duplicate notification prevention, and AFK embed non-recursion.
- **Rollback / grade:** Revert the loop restructuring and post-catch phase extraction separately; retain catch lock. Expected grade **B/B+** after batch and recursion fixes; callback latency remains DB/network dependent.

### A6 — Inventory and release workflow (current grade D+)

- **Evidence / root cause:** release is offloaded at `src/discord/handlers/CreatureReleaseService/CreatureReleaseService.py:19-25`, but `_handle_database_operations` performs release, reward calculation, currency update, and item updates as independent operations at `:36-51`. Zero currency is treated as failure at `src/discord/game_features/creature_inventory/CreatureInventoryManagementView.py:104-109`. Storage expansion passes the view object instead of its integer ID at `src/discord/game_features/creature_inventory/CreatureInventoryView.py:129-135`.
- **Remediation contract:** Make the release unit at `CreatureReleaseService.py:36-51` atomic using the transaction contract from A2; preserve the executor boundary at `:22-25` until a verified async DB API exists. Return an explicit success/result indicator independent of `currency_earned`, and have `_handle_release_operation` (`CreatureInventoryManagementView.py:104-109`) use that indicator so valid zero-currency releases succeed. At `CreatureInventoryView.py:133-134`, pass `self.message_author.user_id` and calculate the expansion cost once per operation; preserve existing confirmation and response text.
- **Behavioral invariants:** already-released creatures are not released again; failed releases do not award currency/items; successful releases with zero currency still show release results; storage payment and expansion update target the confirming user's integer ID.
- **Shared state / risk:** creature release flags, currency, item quantities, selected IDs, and local inventory view state. **THREADING RISK:** all transaction-owned DB calls must execute on the same executor worker/connection unit; no shared `QueryHandler.conn` across workers.
- **New primitives/dependencies:** existing executor and SQLite transaction API proposed in A2; no dependency. A database queue/pool is **APPROVAL REQUIRED**.
- **Tests:** **NO EXISTING TESTS — CREATE.** Atomic rollback after each write failure, zero-currency success, duplicate release race, item reward quantities, and storage expansion user-ID/cost behavior.
- **Rollback / grade:** Revert result-contract, ID, and transaction changes independently. Expected grade **B-/B** after transaction tests; financial correctness remains contingent on A2.

### A7 — Encyclopedia rendering and data fetching (current grade D)

- **Evidence / root cause:** `src/discord/game_features/encyclopedia/EncyclopediaImageFactory.py:123-137` performs two catch-stat queries per creature at `:125-126`; `build_dex_icon` performs an additional first-variant query at `:144-149`. Every render opens multiple assets at `:77-92` and `:154-179`.
- **Remediation contract:** Add bulk read methods beside the existing TGOMMO catch queries that return mappings keyed by `(dex_no|creature_id, environment, time_of_day, mythical)`; load those mappings once in `get_dex_icons` (`:116-137`) and pass values into `build_dex_icon` (`:139-152`). Add a bulk first-variant query or a per-render map for `:144-149`. Preserve filtering predicates and locked/transcendant display rules exactly. Introduce a bounded asset snapshot/cache for the fixed encyclopedia overlays used at `:77-81`, `:97-101`, `:154-170`, but do not share mutable PIL images between renders; use copies.
- **Behavioral invariants:** same icon order, page count, filter state, lock state, first-caught variant, and image output; a missing/zero aggregate must map to the same zero/default behavior as the current query calls.
- **Shared state / risk:** factory fields `creatures`, `dex_icons`, page/filter fields (`:19-37`, `:43-71`) and mutable creature image/variant state (`:141-149`). **THREADING RISK:** shared image objects must never be mutated across concurrent interactions.
- **New primitives/dependencies:** existing SQLite and PIL only. New bulk SQL methods are source changes but not external dependencies; a process-wide image cache is **APPROVAL REQUIRED** unless bounded ownership/eviction is specified.
- **Tests:** **NO EXISTING TESTS — CREATE.** Compare old/new query results, assert query count is O(1) per render rather than O(creatures), verify all filters and first variants, and compare generated image dimensions/content fixtures.
- **Rollback / grade:** Roll back bulk query use while retaining methods; disable image snapshot use independently. Expected grade **B-/B** after query-count measurement; PIL composition remains CPU/IO work.

### A8 — Shop, trap, and item interaction paths (current grade C)

- **Evidence / root cause:** `interaction_guard` bypasses locking when called without a view at `src/commons/CommonDecorators.py:49-54`; shop callback uses `@interaction_guard()` at `src/discord/game_features/shop/ShopView.py:31-33`. Shop rendering performs per-item/per-avatar DB checks at `src/discord/game_features/shop/ShopImageFactory.py:50-63`. Trap selection holds `_TRAP_MAP_LOCK` while DB reads/filtering at `src/discord/handlers/ItemUseHandler/TrapHandler.py:27-54`.
- **Remediation contract:** Bind the decorator to the view instance at `ShopView.py:31-33` and every equivalent callback, or use the existing `check_if_user_can_interact_with_view`/`asyncio.Lock` pattern already present in `CreatureEncounterView.py:52-61`; preserve deferred-response and retry settings. For `ShopImageFactory.py:50-63`, collect ownership/purchase status in one render snapshot before image composition, preserving each item's sold-out predicate. In `TrapHandler.py:27-54`, move DB reads outside `_TRAP_MAP_LOCK`; hold the lock only while publishing/reading the minimal in-process selection map, and preserve eligibility/filter ordering. **NEEDS REVIEW:** confirm whether trap data can change between snapshot and final charge; if yes, enforce a DB-side conditional update rather than trusting the snapshot.
- **Behavioral invariants:** unauthorized users remain rejected; one view interaction is serialized; shop sold-out state remains user/date-specific; trap selection remains rarity-prioritized and basic-trap fallback remains unchanged.
- **Shared state / risk:** view `interaction_lock`, `message_author`, shop state, `_TRAP_MAP_LOCK`, trap map, user inventory and avatar ownership. **THREADING RISK:** do not hold a process lock across blocking DB calls; DB atomicity belongs to A2.
- **New primitives/dependencies:** existing locks and DB APIs only. A new cache or conditional SQL statement is **APPROVAL REQUIRED** until query/schema impact is reviewed.
- **Tests:** **NO EXISTING TESTS — CREATE.** Guard rejection/serialization, shop query-count and date behavior, trap lock duration, rarity fallback, and concurrent charge/selection races.
- **Rollback / grade:** Revert decorator binding, shop snapshot, and trap lock-scope changes separately. Expected grade **B/B+** after lock and N+1 validation.

### A9 — JSON game-state persistence (current grade C)

- **Evidence / root cause:** `GameStateManager` owns an `RLock` at `src/commons/GameStateManager.py:25-29`, but most getters/setters load and save outside it, e.g. getters `:87-123` and setters `:163-213`. Atomic replacement exists at `:67-75`; shop loops use `state.get("current_shop_item_ids")` without a default at `:104-123`.
- **Remediation contract:** Keep atomic `_save_state` replacement at `:67-75`. Wrap each read-modify-write setter (`:163-213`) and any getter that composes mutable state (`:104-123`, `:147-159`) in the existing `self._lock`; for compound operations, load once, modify once, save once. Use safe defaults for optional lists at `:110` and `:119` (`state.get(..., [])`) without changing valid-state output. Add explicit locked update methods for callers that currently perform get-then-set across separate public calls; migrate only those call sites after inventorying them.
- **Behavioral invariants:** persisted JSON keys and formats remain compatible; atomic replace remains; missing optional lists yield empty results rather than exceptions; concurrent updates do not silently overwrite each other.
- **Shared state / risk:** JSON file, `_lock`, global `game_state_manager` (`:11-23`), cache-resolved item/avatar objects. **THREADING RISK:** all file read/write operations must use the same manager lock; external processes are not protected by this in-process lock and require a separate file-lock decision.
- **New primitives/dependencies:** existing `threading.RLock` only. A cross-process file lock, journal, or SQLite migration is **APPROVAL REQUIRED**.
- **Tests:** **NO EXISTING TESTS — CREATE.** Concurrent setter stress, malformed/missing state, atomic-save failure cleanup, default-list behavior, and preservation of unrelated keys during updates.
- **Rollback / grade:** Revert lock coverage and caller migration independently; retain safe defaults if compatible. Expected grade **B/B+** for in-process concurrency; cross-process writers remain a residual risk.

### A10 — Object construction and media loading (current grade D)

- **Evidence / root cause:** `TGOCreature.define_creature_images` decodes/copies two images in constructors/rarity changes at `src/discord/objects/TGOCreature.py:83-109`. `TGOAvatar.define_avatar_images` decodes avatar/icon/quest images and constructs image factories at `src/discord/objects/TGOAvatar.py:57-80`. `TGOPlayerItem.define_item_image` decodes and builds unlock imagery at `src/discord/objects/TGOPlayerItem.py:38-51`. `TGOPlayer.define_user_display_creatures` performs up to six DB calls at `src/discord/objects/TGOPlayer.py:44-53`.
- **Remediation contract:** Separate metadata construction from media materialization: retain current public object fields and fallback selection, but defer `Image.open`/copy and derived image-factory generation until a rendering method requests them. Add a bounded, immutable-by-caller asset cache only after measuring memory and invalidation needs; cached images must be copied before mutation. Replace the six independent display-creature calls at `TGOPlayer.py:44-53` with one bulk DB method or one existing query that returns the same six slot results in order. **REQUIRES TRADEOFF:** lazy media changes when missing-asset errors/logs occur and may shift latency from construction to first render; preserve eager behavior instead if compatibility tests require it.
- **Behavioral invariants:** fallback assets, rarity/variant image selection, display-slot ordering, and image dimensions remain identical; object construction without rendering must retain all metadata fields.
- **Shared state / risk:** PIL image objects on domain instances, asset cache entries, display-creature list. **THREADING RISK:** PIL objects are mutable; never expose a shared cached instance for in-place paste/draw.
- **New primitives/dependencies:** existing PIL and filesystem only. A new cache implementation is **APPROVAL REQUIRED** unless bounded size, eviction, and invalidation are specified.
- **Tests:** **NO EXISTING TESTS — CREATE.** Constructor timing, first-render timing, fallback paths, object field compatibility, image equality fixtures, cache-copy isolation, and display query count/order.
- **Rollback / grade:** Revert lazy materialization and bulk display query independently. Expected grade **B-/B** after memory/query profiling; render CPU remains.

### A11 — Deprecated surface (`src/zz_deprecated`) (current grade B-)

- **Evidence / root cause:** Audit search found the deprecated tree isolated from active runtime imports, with an internal import at `src/zz_deprecated/twitch/TwitchBot.py:5`; the risk is maintenance/dependency drift rather than a measured hot path.
- **Remediation contract:** Produce an import/reference inventory for `src/zz_deprecated`, mark each module as archived, retained for manual tooling, or removable, and exclude archived modules from lint/type/test discovery and packaging only after verifying no active import. Document the retention/removal decision in the repository. Do not delete code as part of this specification.
- **Behavioral invariants:** active runtime imports and deployment artifacts remain unchanged; manual deprecated tooling is not silently removed; no dependency used by active `src/` is removed.
- **Shared state / risk:** packaging/tool configuration and any import side effects. **NEEDS REVIEW:** no full packaging configuration or runtime import graph was established by the static audit.
- **New primitives/dependencies:** existing search/lint/package exclusion mechanisms only. Removing dependencies or deleting the tree is **APPROVAL REQUIRED**.
- **Tests:** **NO EXISTING TESTS — CREATE.** Import active modules in a clean environment, run the configured test/lint discovery, and verify deprecated modules are excluded only where intended.
- **Rollback / grade:** Revert exclusion/documentation configuration without restoring deleted code. Expected grade remains **B**; this area has low runtime impact and high maintenance benefit.

## 3. Cross-Area Shared-State and Dependency Matrix

| Resource | Primary areas | Required protection |
|---|---:|---|
| Discord event loop and startup thread | A1, A5, A8, A10 | One lifecycle owner; no synchronous DB/PIL work added to async callbacks without an executor decision. |
| Global DB handler / `QueryHandler.conn` and `.cursor` | A1, A2, A5, A6, A7, A8 | Never share mutable connection/cursor concurrently; transactions own their connection scope. |
| Game-state JSON and `GameStateManager._lock` | A1, A8, A9 | All in-process read-modify-write operations use the existing lock; preserve atomic replace. |
| Static cache registry/snapshots | A1, A3, A5, A10 | Publish immutable snapshots under existing locks; no mutable PIL object sharing. |
| Discord view locks and callbacks | A5, A6, A8 | Preserve user authorization and single-interaction semantics. |
| PIL images/assets | A5, A7, A10 | Copies for mutation; cache only with explicit bounds/invalidation. |

## 4. Remediation Ordering

1. **A2 database transaction/connection contract** — establishes safe primitives for A5, A6, A7, A8, and A9 caller changes.
2. **A9 JSON lock coverage** and **A3 provider/logging fixes** — low-risk state/cache correctness improvements.
3. **A6 release correctness** and **A8 interaction guard/lock scope** — protect user-visible economy and concurrency behavior.
4. **A5 catch/unlock batching** — deploy after transaction and callback tests exist.
5. **A7 encyclopedia bulk reads** — requires query result parity fixtures.
6. **A10 object/media strategy** — deploy only after image compatibility and memory measurements.
7. **A1 lifecycle/logging** — verify Discord loop ownership before changing startup thread behavior.
8. **A11 deprecated-surface exclusions** — last, after import and packaging inventory.

## 5. Portfolio Test and Rollback Gates

- Each area must have a focused regression suite before implementation is considered complete; current audit evidence indicates **NO EXISTING TESTS — CREATE** for these performance contracts.
- Compare baseline and candidate query counts, callback latency, image decode counts, memory, lock wait, and error rates under representative manual/load scenarios.
- Do not combine A2 transaction migration with A10 lazy media migration in one rollback unit.
- Preserve the existing `documentation/CREATURE_SPAWN_REMEDIATION_SPEC.md` independently; this document does not authorize changes to the Creature Spawn/Despawn Pipeline.

## 6. Open Questions / Approval Gates

- **NEEDS REVIEW:** whether Discord startup must remain on a dedicated thread and which loop owns `AsyncIOScheduler`.
- **NEEDS REVIEW:** whether SQLite writes may be serialized through one connection or require per-worker connections; do not assume a pool.
- **REQUIRES TRADEOFF:** lazy media loading changes when work and failures occur; choose eager compatibility versus deferred latency explicitly.
- **REQUIRES TRADEOFF:** awaiting Discord sends would improve error visibility but changes callback ordering; no background fan-out is authorized here.
- **APPROVAL REQUIRED:** external libraries, connection pools, async SQLite drivers, cross-process file locks, schema migrations, new image caches, and deletion of deprecated code.
- **Residual risk:** this remains a static specification. Runtime Discord jitter, SQLite lock contention, PIL memory, and production traffic must be measured after implementation.


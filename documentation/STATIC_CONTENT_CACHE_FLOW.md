# Static Content Cache Flow

This document explains the exact startup and cache-loading logic for the new static-content cache framework, starting from `src/Main.py` and following the concrete environment-creature cache path.

## High-level purpose

The goal of this layer is to load static DB content once, build immutable in-memory snapshots, and serve fast read-only lookups afterward.

For the current proof of concept, the only registered cache is `EnvironmentCreatureCache`.

---

## Startup call chain

The runtime entry point is:

```python
asyncio.run(main())
```

### 1) `src/Main.py` → `main()`

`main()` is the top-level startup coroutine.

It runs these steps in order:

1. `initialize_project_directories()`
2. `initialize_database()`
3. `initialize_static_content_cache_registry(get_tgommo_db_handler)`
4. `await StartupCacheInitializer().initialize_async()`
5. `initialize_game_state_manager()`
6. Start the Discord bot thread if `RUN_DISCORD_BOT` is enabled

So the cache system is intentionally initialized **after** the DB handler exists and **before** the rest of the app begins normal runtime work.

---

## Database initialization step

### 2) `initialize_database()`

Defined in `src/database/handlers/DatabaseHandler.py`.

This creates the global database handler instance and sets up the module-level accessors:

- `get_db_handler()`
- `get_tgommo_db_handler()`
- `get_user_db_handler()`

For the cache framework, the important part is that `get_tgommo_db_handler()` becomes available and can be passed into the registry initializer.

---

## Cache registry initialization

### 3) `initialize_static_content_cache_registry(get_tgommo_db_handler)`

Defined in `src/caching/registry.py`.

This method creates the singleton-style registry and registers the eager caches.

Exact flow:

1. `initialize_static_content_cache_registry(...)`
2. `StaticContentCacheRegistry()`
3. `registry.register(EnvironmentCreatureCache(db_provider=get_tgommo_db_handler, logger=logger))`
4. Store the registry in the module-level `_cache_registry`

### Why a provider function is passed in

The cache does not call the DB handler directly at import time.
Instead, it receives `get_tgommo_db_handler` as a callable and resolves the handler only when loading.

That keeps startup ordering safe:

- database first
- cache registry second
- cache load third

---

## Startup eager-load step

### 4) `StartupCacheInitializer().initialize_async()`

Defined in `src/caching/startup.py`.

This is the startup hook that warms eager caches without blocking the event loop.

Exact flow:

1. `StartupCacheInitializer.__init__()`
2. `StartupCacheInitializer.initialize_async()`
3. `StartupCacheInitializer.initialize()` via `asyncio.to_thread(...)`
4. `StaticContentCacheRegistry.eager_caches()`
5. For each eager cache, call `StaticContentCacheBase._reload_snapshot()`

### Why `initialize_async()` exists

The startup initializer has both sync and async paths so the same cache framework can be used in:

- synchronous startup paths
- async startup paths
- future hosted-service style entry points

For now, `main()` uses the async form:

```python
await StartupCacheInitializer().initialize_async()
```

---

## Base cache reload logic

### 5) `StaticContentCacheBase._reload_snapshot()`

Defined in `src/caching/base.py`.

This is the shared reload path used by framework code.

Exact flow:

1. Record the start time
2. Call the subclass hook `_load_snapshot()`
3. Store the returned snapshot under a lock
4. Log the load duration
5. Return the loaded snapshot

This method is the shared mechanism for:

- startup eager loading
- future refresh operations
- future lazy-loading support

### Thread-safety behavior

`StaticContentCacheBase` uses a lock around snapshot replacement, so readers always see either the old snapshot or the new snapshot, never a partially built one.

---

## Concrete cache load

### 6) `EnvironmentCreatureCache._load_snapshot()`

Defined in `src/caching/environment_creature_cache.py`.

This is the concrete POC cache that builds the environment-creature indexes.

Exact flow:

1. `EnvironmentCreatureCache._load_snapshot()`
2. `db = self._db_provider()`
3. Call bulk loaders only:
   - `TGOMMODatabaseHandler.get_all_creatures(convert_to_object=True)`
   - `TGOMMODatabaseHandler.get_all_environment_creatures(convert_to_object=True)`
   - `TGOMMODatabaseHandler.get_all_environments_in_rotation(is_day_night=0, convert_to_object=True)`
   - `TGOMMODatabaseHandler.get_all_environments_in_rotation(is_day_night=1, convert_to_object=True)`
4. Build immutable indexes
5. Return `EnvironmentCreatureCacheSnapshot`

### Important constraint

This cache does **not** call single-row lookup methods in a loop.
It uses the existing bulk loaders as-is and shapes the data in memory.

---

## How the cache derives the indexes

### Source data

The cache loads:

- all creatures
- all environment-creature links
- both day and night environment variants

It uses the environment rows to infer which environment ID belongs to the day bucket or the night bucket.

### Snapshot fields

`EnvironmentCreatureCacheSnapshot` contains four immutable structures:

1. `creatures_by_environment_and_spawn`
   - Equivalent to `Dictionary<(Environment, SpawnTime), List<Creature>>`
   - In Python it is stored as a mapping of tuples to tuples

2. `creatures_by_environment`
   - Equivalent to `Dictionary<Environment, List<Creature>>`
   - Deduplicated so a creature that appears in both day and night buckets is only listed once for the environment

3. `creatures_by_id`
   - Equivalent to `Dictionary<CreatureId, Creature>`

4. `spawn_membership`
   - Equivalent to `HashSet<(CreatureId, Environment, SpawnTime)>`
   - Used for fast membership checks like "can this creature spawn in Iceland at night?"

### BOTH spawn handling

If the requested spawn time is `BOTH`, `EnvironmentCreatureCache.get_creatures()` merges the day and night buckets and deduplicates them.

That means:

- `DAY` bucket returns only day-linked rows
- `NIGHT` bucket returns only night-linked rows
- `BOTH` returns the union without duplicates
- the deduplicated environment list still contains each creature only once

---

## Post-load read path

After startup, consumers read from the cache through these methods:

- `EnvironmentCreatureCache.get_creatures(environment, spawn_time)`
- `EnvironmentCreatureCache.get_all_creatures_for_environment(environment)`
- `EnvironmentCreatureCache.get_creature_by_id(creature_id)`
- `EnvironmentCreatureCache.can_creature_spawn(creature_id, environment, spawn_time)`

These methods read directly from the immutable snapshot and do not hit the database.

### Lazy-loading readiness

The base class already supports future lazy loading because `snapshot` uses the shared `_ensure_loaded()` path.

That means a later cache can switch to `CacheLoadStrategy.LAZY` without rewriting the thread-safety or snapshot semantics.

---

## Refresh flow

When a refresh is needed, the framework calls the same internal reload path again:

1. `StaticContentCacheRegistry.refresh_all()`
2. `StaticContentCacheBase._reload_snapshot()` for each registered cache
3. `EnvironmentCreatureCache._load_snapshot()` rebuilds the snapshot
4. The new snapshot replaces the old one atomically

So refresh is a full rebuild, not an incremental patch.

---

## Exact method-name chain summary

### Startup path

```text
asyncio.run(main())
  -> main()
    -> initialize_project_directories()
    -> initialize_database()
    -> initialize_static_content_cache_registry(get_tgommo_db_handler)
      -> StaticContentCacheRegistry()
      -> register(EnvironmentCreatureCache(...))
    -> StartupCacheInitializer.__init__()
    -> StartupCacheInitializer.initialize_async()
      -> StartupCacheInitializer.initialize()
        -> StaticContentCacheRegistry.eager_caches()
        -> StaticContentCacheBase._reload_snapshot()
          -> EnvironmentCreatureCache._load_snapshot()
            -> get_tgommo_db_handler()
            -> TGOMMODatabaseHandler.get_all_creatures()
            -> TGOMMODatabaseHandler.get_all_environment_creatures()
            -> TGOMMODatabaseHandler.get_all_environments_in_rotation()
```

### Read path

```text
consumer
  -> resolve_static_content_cache(EnvironmentCreatureCache)
  -> EnvironmentCreatureCache.get_creatures(...)
     or EnvironmentCreatureCache.get_all_creatures_for_environment(...)
     or EnvironmentCreatureCache.get_creature_by_id(...)
     or EnvironmentCreatureCache.can_creature_spawn(...)
```

---

## What would change for lazy loading later

To add lazy loading later, the framework would mainly change at the strategy level:

- set `load_strategy=CacheLoadStrategy.LAZY` on the cache
- let `snapshot` trigger `_ensure_loaded()` on first access
- keep the same `_load_snapshot()` implementation
- keep the same immutable snapshot and locking behavior

So the eager path used in this POC is already compatible with a future lazy or hybrid model.


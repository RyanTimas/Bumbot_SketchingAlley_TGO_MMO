import threading
from typing import Any, Callable, Optional, Type, cast

from src.caching.cache_base import CacheLoadStrategy, IStaticContentCache, IStaticContentCacheRegistry
from src.caching.db_specific_caches.environment_creature_cache import EnvironmentCreatureCache
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler

class StaticContentCacheRegistry(IStaticContentCacheRegistry):
    """Simple in-memory registry for static-content cache instances."""

    def __init__(self):
        self._lock = threading.RLock()
        self._caches: list[IStaticContentCache[Any]] = []

    def register(self, cache: IStaticContentCache[Any]) -> IStaticContentCache[Any]:
        with self._lock:
            for existing in self._caches:
                if existing.__class__ is cache.__class__:
                    return existing
            self._caches.append(cache)
            return cache

    def resolve(self, cache_type: type) -> IStaticContentCache[Any]:
        cache = self.resolve_optional(cache_type)
        if cache is None:
            raise KeyError(f"No static-content cache registered for type {cache_type!r}")
        return cache

    def resolve_optional(self, cache_type: type) -> Optional[IStaticContentCache[Any]]:
        with self._lock:
            for cache in self._caches:
                if isinstance(cache, cache_type):
                    return cast(IStaticContentCache[Any], cache)
        return None

    def eager_caches(self) -> tuple[IStaticContentCache[Any], ...]:
        with self._lock:
            return tuple(cache for cache in self._caches if cache.load_strategy == CacheLoadStrategy.EAGER)

    def all_caches(self) -> tuple[IStaticContentCache[Any], ...]:
        with self._lock:
            return tuple(self._caches)

    def refresh_all(self) -> None:
        for cache in self.all_caches():
            cache.reload_snapshot()

    def register_factory(self, factory: Callable[[], IStaticContentCache[Any]]) -> IStaticContentCache[Any]:
        return self.register(factory())


_cache_registry: Optional[StaticContentCacheRegistry] = None
_cache_registry_lock = threading.RLock()

# REGISTER INDIVIDUAL CACHES HERE
def initialize_static_content_cache_registry(logger=None, db_provider= None) -> StaticContentCacheRegistry:
    db_provider = db_provider if db_provider else get_tgommo_db_handler

    global _cache_registry
    with _cache_registry_lock:
        registry = StaticContentCacheRegistry()

        # Register eager caches
        registry.register(EnvironmentCreatureCache(db_provider=db_provider, logger=logger))

        _cache_registry = registry
        return registry

def get_static_content_cache_registry() -> StaticContentCacheRegistry:
    """Return the initialized cache registry."""
    with _cache_registry_lock:
        if _cache_registry is None:
            raise RuntimeError("Static content cache registry not initialized.")
        return _cache_registry

def resolve_static_content_cache(cache_type: Type[Any]) -> IStaticContentCache[Any]:
    """Convenience wrapper for resolving a cache by type."""
    return get_static_content_cache_registry().resolve(cache_type)



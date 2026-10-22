import threading
import logging
from typing import Any, Callable, Optional, Type, cast

from src.caching.cache_base import CacheLoadStrategy, IStaticContentCache, IStaticContentCacheRegistry
from src.caching.db_specific_caches.avatar_cache import AvatarCache
from src.caching.db_specific_caches.creature_cache import CreatureCache
from src.caching.db_specific_caches.environment_cache import EnvironmentCache
from src.caching.db_specific_caches.environment_creature_cache import EnvironmentCreatureCache
from src.caching.db_specific_caches.player_state_cache import PlayerStateCache
from src.caching.db_specific_caches.quest_collection_cache import QuestCollectionCache
from src.caching.db_specific_caches.static_item_cache import StaticItemCache
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler

class StaticContentCacheRegistry(IStaticContentCacheRegistry):
    """Simple in-memory registry for static-content cache instances."""

    def __init__(self):
        self._lock = threading.RLock()
        self._caches: list[IStaticContentCache[Any]] = []

    # region static-content cache registry methods
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
    # endregion

_cache_registry: Optional[StaticContentCacheRegistry] = None
_cache_registry_lock = threading.RLock()

# REGISTER INDIVIDUAL CACHES HERE
def initialize_static_content_cache_registry(logger=None, db_provider= None) -> StaticContentCacheRegistry:
    db_provider = db_provider if db_provider else get_tgommo_db_handler

    global _cache_registry
    with _cache_registry_lock:
        if _cache_registry is not None:
            if logger:
                logger.info("Static content cache registry already initialized; reusing existing registry.")
            return _cache_registry

        registry = StaticContentCacheRegistry()

        # REGISTER EAGER CACHES HERE - MODIFY THIS LIST AS NEEDED
        registry.register(CreatureCache(db_provider=db_provider, logger=logger))
        registry.register(EnvironmentCache(db_provider=db_provider, logger=logger))
        registry.register(QuestCollectionCache(db_provider=db_provider, logger=logger))
        registry.register(EnvironmentCreatureCache(db_provider=db_provider, logger=logger))
        registry.register(AvatarCache(db_provider=db_provider, logger=logger))
        registry.register(PlayerStateCache(db_provider=db_provider, logger=logger))
        registry.register(StaticItemCache(db_provider=db_provider, logger=logger))

        _cache_registry = registry

        if logger:
            logger.info("Static content cache registry initialized with %s cache type(s).", len(registry.all_caches()))
        return registry


def is_static_content_cache_registry_initialized() -> bool:
    with _cache_registry_lock:
        return _cache_registry is not None


def ensure_static_content_cache_registry_initialized(logger: logging.Logger | None = None, db_provider=None) -> StaticContentCacheRegistry:
    with _cache_registry_lock:
        if _cache_registry is not None:
            return _cache_registry

    return initialize_static_content_cache_registry(logger=logger, db_provider=db_provider)

def get_static_content_cache_registry() -> StaticContentCacheRegistry:
    """Return the initialized cache registry."""
    with _cache_registry_lock:
        if _cache_registry is None:
            raise RuntimeError("Static content cache registry not initialized.")
        return _cache_registry

def resolve_static_content_cache(cache_type: Type[Any]) -> IStaticContentCache[Any]:
    """Convenience wrapper for resolving a cache by type."""
    registry = ensure_static_content_cache_registry_initialized()
    return registry.resolve(cache_type)



import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, cast

from src.caching.cache_base import IStaticContentCacheRegistry, StaticContentCacheBase
from src.caching.cache_registry import get_static_content_cache_registry


class IStartupCacheInitializer(ABC):
    """Startup hook that eagerly warms all registered eager caches."""

    @abstractmethod
    def initialize(self) -> None:
        """Load eager caches synchronously."""

    @abstractmethod
    async def initialize_async(self) -> None:
        """Load eager caches without blocking the event loop."""


class StartupCacheInitializer(IStartupCacheInitializer):
    """Eager startup initializer for static-content caches."""

    def __init__(self, registry: IStaticContentCacheRegistry | None = None, logger: logging.Logger | None = None):
        self._registry = registry or get_static_content_cache_registry()
        self._logger = logger or logging.getLogger(self.__class__.__module__)

    def initialize(self) -> None:
        caches = self._registry.eager_caches()
        self._logger.info("Eager-loading %s static-content cache(s).", len(caches))
        for cache in caches:
            cast(StaticContentCacheBase[Any], cache).reload_snapshot()

    async def initialize_async(self) -> None:
        await asyncio.to_thread(self.initialize)



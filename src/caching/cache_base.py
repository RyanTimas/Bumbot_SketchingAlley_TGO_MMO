import logging
import threading
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from src.commons.CommonDecorators import measure_execution_time

TSnapshot = TypeVar("TSnapshot")


class CacheLoadStrategy(Enum):
    """Loading mode for a static-content cache."""

    EAGER = "eager"
    LAZY = "lazy"


class IStaticContentCache(ABC, Generic[TSnapshot]):
    """Interface for a read-mostly, static-content cache."""

    @property
    @abstractmethod
    def cache_name(self) -> str:
        """Human-readable cache name used for logging."""

    @property
    @abstractmethod
    def load_strategy(self) -> CacheLoadStrategy:
        """Loading strategy used by the cache."""

    @property
    @abstractmethod
    def snapshot(self) -> TSnapshot:
        """Return the current immutable snapshot, loading it if necessary."""

    @abstractmethod
    def is_loaded(self) -> bool:
        """Return whether the cache currently has a loaded snapshot."""

    @abstractmethod
    def reload_snapshot(self) -> TSnapshot:
        """Reload the cache snapshot. Framework code calls this; consumers should not."""


class StaticContentCacheBase(IStaticContentCache[TSnapshot], ABC):
    """Shared thread-safe loading/refreshing behavior for static-content caches.

    The base class uses a double-checked lock around a snapshot reference so the
    same mechanism can support eager startup loading today and lazy loading later.
    """

    def __init__(self, load_strategy: CacheLoadStrategy = CacheLoadStrategy.EAGER, logger: Optional[logging.Logger] = None):
        self._load_strategy = load_strategy
        self._logger = logger or logging.getLogger(self.__class__.__module__)
        self._lock = threading.RLock()
        self._snapshot: Optional[TSnapshot] = None

    ''' ----- PROPERTIES ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # region properties
    @property
    def cache_name(self) -> str:
        return self.__class__.__name__

    @property
    def load_strategy(self) -> CacheLoadStrategy:
        return self._load_strategy

    @property
    def snapshot(self) -> TSnapshot:
        return self._ensure_loaded()

    def is_loaded(self) -> bool:
        return self._snapshot is not None

    def _ensure_loaded(self) -> TSnapshot:
        if self._snapshot is None:
            self.reload_snapshot()
        return self._snapshot
    # endregion


    ''' ----- SNAPSHOT FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def reload_snapshot(self) -> TSnapshot:
        print(f"Reloading snapshot for cache: {self.cache_name}")
        snapshot = self._load_snapshot()
        with self._lock:
            self._snapshot = snapshot
        return snapshot

    @measure_execution_time
    def _invalidate_snapshot(self) -> None:
        with self._lock:
            self._snapshot = None

    @abstractmethod
    def _load_snapshot(self) -> TSnapshot:
        """Load and build a new immutable snapshot from the backing data source."""


class IStaticContentCacheRegistry(ABC):
    """Registry/manager abstraction for resolving caches by type."""

    @abstractmethod
    def register(self, cache: IStaticContentCache[Any]) -> IStaticContentCache[Any]:
        """Register a cache instance and return it."""

    @abstractmethod
    def resolve(self, cache_type: type) -> IStaticContentCache[Any]:
        """Resolve a cache by its concrete class or interface type."""

    @abstractmethod
    def resolve_optional(self, cache_type: type) -> Optional[IStaticContentCache[Any]]:
        """Resolve a cache by type, returning None when not registered."""

    @abstractmethod
    def eager_caches(self) -> tuple[IStaticContentCache[Any], ...]:
        """Return all caches configured for eager startup loading."""

    @abstractmethod
    def all_caches(self) -> tuple[IStaticContentCache[Any], ...]:
        """Return every registered cache instance."""

    @abstractmethod
    def refresh_all(self) -> None:
        """Reload every registered cache snapshot."""


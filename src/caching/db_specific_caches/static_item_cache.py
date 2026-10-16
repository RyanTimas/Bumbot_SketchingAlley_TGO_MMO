from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Optional, Tuple

from src.caching.cache_base import CacheLoadStrategy, StaticContentCacheBase
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOPlayerItem import TGOPlayerItem


@dataclass(frozen=True, slots=True)
class StaticItemCacheSnapshot:
    """Immutable snapshot for static item lookups."""

    all_items: Tuple[TGOPlayerItem, ...]
    items_by_id: Mapping[int, TGOPlayerItem]


class StaticItemCache(StaticContentCacheBase[StaticItemCacheSnapshot]):
    """Static-content cache for inventory item lookups.

    The cache eagerly loads every item definition from tgommo_inventory_item at
    startup so callers can resolve item metadata and images without hitting the
    database repeatedly.
    """

    def __init__(self, db_provider=None, logger=None, load_strategy: CacheLoadStrategy = CacheLoadStrategy.EAGER):
        super().__init__(load_strategy=load_strategy, logger=logger)
        self._db_provider = db_provider or get_tgommo_db_handler

    def _load_snapshot(self) -> StaticItemCacheSnapshot:
        all_items = get_tgommo_db_handler().get_all_base_items() or []

        items_by_id = {item.item_id: item for item in all_items}
        return StaticItemCacheSnapshot(all_items=tuple(all_items), items_by_id=MappingProxyType(items_by_id),)

    ''' ---- GETTERS ----------------------------------------------------------------------------------------------------------------------------'''
    def get_item_by_id(self, item_id: int) -> Optional[TGOPlayerItem]:
        """Return a cached item definition by item ID."""
        return self.snapshot.items_by_id.get(item_id)

    def get_all_items(self) -> tuple[TGOPlayerItem, ...]:
        """Return every cached item definition."""
        return self.snapshot.all_items

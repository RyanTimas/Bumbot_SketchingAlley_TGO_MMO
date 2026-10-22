from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from src.caching.cache_base import CacheLoadStrategy, StaticContentCacheBase
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOAvatar import TGOAvatar
from src.discord.objects.TGOCollection import TGOCollection


@dataclass(frozen=True, slots=True)
class QuestCollectionCacheSnapshot:
    """Immutable snapshot for collection and default quest-avatar lookups."""

    collection_by_collection_id: Tuple[TGOCollection, ...]
    active_collections: Tuple[TGOCollection, ...]
    avatars_with_unlock_conditions: Tuple[TGOAvatar, ...]
    avatars_by_nickname: Mapping[str, Tuple[TGOAvatar, ...]]


class QuestCollectionCache(StaticContentCacheBase[QuestCollectionCacheSnapshot]):
    """Cache wrapper for collections and avatar quest/nickname queries."""

    def __init__(self, db_provider=None, logger=None, load_strategy: CacheLoadStrategy = CacheLoadStrategy.LAZY):
        super().__init__(load_strategy=load_strategy, logger=logger)
        self._db_provider = db_provider or get_tgommo_db_handler

    def _load_snapshot(self) -> QuestCollectionCacheSnapshot:
        db = self._db_provider()

        collection_by_collection_id = db.get_collection_by_collection_id(convert_to_object=True) or []
        active_collections = db.get_active_collections(convert_to_object=True) or []
        avatars_with_unlock_conditions = db.get_avatars_with_unlock_conditions(
            exclude_unlocked_avatars=False,
            user_id=1,
            convert_to_object=True,
        ) or []

        avatars_by_nickname: dict[str, list[TGOAvatar]] = {}
        for avatar in avatars_with_unlock_conditions:
            nickname = (avatar.name or "").strip().lower()
            if not nickname:
                continue
            avatars_by_nickname.setdefault(nickname, []).append(avatar)

        return QuestCollectionCacheSnapshot(
            collection_by_collection_id=tuple(collection_by_collection_id),
            active_collections=tuple(active_collections),
            avatars_with_unlock_conditions=tuple(avatars_with_unlock_conditions),
            avatars_by_nickname=MappingProxyType({key: tuple(value) for key, value in avatars_by_nickname.items()}),
        )

    def get_collection_by_collection_id(self, convert_to_object=False):
        if not convert_to_object:
            return self._db_provider().get_collection_by_collection_id(convert_to_object=False)
        return list(self.snapshot.collection_by_collection_id)

    def get_active_collections(self, convert_to_object=False):
        if not convert_to_object:
            return self._db_provider().get_active_collections(convert_to_object=False)
        return list(self.snapshot.active_collections)

    def get_avatars_with_unlock_conditions(self, exclude_unlocked_avatars=False, user_id=1, convert_to_object=True):
        if not exclude_unlocked_avatars and convert_to_object:
            return list(self.snapshot.avatars_with_unlock_conditions)
        return self._db_provider().get_avatars_with_unlock_conditions(
            exclude_unlocked_avatars=exclude_unlocked_avatars,
            user_id=user_id,
            convert_to_object=convert_to_object,
        )

    def get_avatars_by_nickname(self, nickname='', exclude_unlocked_avatars=False, user_id=1, convert_to_object=True):
        if not exclude_unlocked_avatars and convert_to_object:
            cached = self.snapshot.avatars_by_nickname.get((nickname or '').strip().lower())
            if cached is not None:
                return list(cached)
        return self._db_provider().get_avatars_by_nickname(
            nickname=nickname,
            exclude_unlocked_avatars=exclude_unlocked_avatars,
            user_id=user_id,
            convert_to_object=convert_to_object,
        )


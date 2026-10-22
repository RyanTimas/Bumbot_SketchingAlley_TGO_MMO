from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from src.caching.cache_base import CacheLoadStrategy, StaticContentCacheBase
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOAvatar import TGOAvatar


@dataclass(frozen=True, slots=True)
class AvatarCacheSnapshot:
    """Immutable snapshot for static avatar lookups."""

    limited_time_avatars: Tuple[TGOAvatar, ...]
    limited_time_avatars_by_id: Mapping[int, TGOAvatar]


class AvatarCache(StaticContentCacheBase[AvatarCacheSnapshot]):
    """Cache wrapper for avatar queries."""

    def __init__(self, db_provider=None, logger=None, load_strategy: CacheLoadStrategy = CacheLoadStrategy.LAZY):
        super().__init__(load_strategy=load_strategy, logger=logger)
        self._db_provider = db_provider or get_tgommo_db_handler

    def _load_snapshot(self) -> AvatarCacheSnapshot:
        db = self._db_provider()
        limited_time_avatars = db.get_all_limited_time_avatars(convert_to_object=True) or []

        return AvatarCacheSnapshot(
            limited_time_avatars=tuple(limited_time_avatars),
            limited_time_avatars_by_id=MappingProxyType({avatar.avatar_id: avatar for avatar in limited_time_avatars}),
        )

    def get_avatar_by_id(self, avatar_id, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_avatar_by_id(avatar_id=avatar_id, convert_to_object=False)

        cached = self.snapshot.limited_time_avatars_by_id.get(avatar_id)
        if cached is not None:
            return cached
        return self._db_provider().get_avatar_by_id(avatar_id=avatar_id, convert_to_object=True)

    def get_child_avatars_by_parent_id(self, parent_avatar_id=''):
        return self._db_provider().get_child_avatars_by_parent_id(parent_avatar_id=parent_avatar_id)

    def get_all_limited_time_avatars(self, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_all_limited_time_avatars(convert_to_object=False)
        return list(self.snapshot.limited_time_avatars)

    def get_currently_available_limited_time_avatars(self, exclude_unlocked_avatars=False, user_id=1, convert_to_object=True):
        return self._db_provider().get_currently_available_limited_time_avatars(
            exclude_unlocked_avatars=exclude_unlocked_avatars,
            user_id=user_id,
            convert_to_object=convert_to_object,
        )

    def get_random_shop_avatars(self, count=3, convert_to_object=True):
        return self._db_provider().get_random_shop_avatars(count=count, convert_to_object=convert_to_object)


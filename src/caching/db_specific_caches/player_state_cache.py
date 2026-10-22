from dataclasses import dataclass

from src.caching.cache_base import CacheLoadStrategy, StaticContentCacheBase
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler


@dataclass(frozen=True, slots=True)
class PlayerStateCacheSnapshot:
	"""Placeholder snapshot for player-state cache wrappers."""

	initialized: bool


class PlayerStateCache(StaticContentCacheBase[PlayerStateCacheSnapshot]):
	"""Wrapper cache for player/profile/inventory/avatar-link/trap-link methods."""

	def __init__(self, db_provider=None, logger=None, load_strategy: CacheLoadStrategy = CacheLoadStrategy.LAZY):
		super().__init__(load_strategy=load_strategy, logger=logger)
		self._db_provider = db_provider or get_tgommo_db_handler

	def _load_snapshot(self) -> PlayerStateCacheSnapshot:
		# Live player-state methods remain pass-through to avoid stale mutable user data.
		return PlayerStateCacheSnapshot(initialized=True)

	def get_user_profile_by_user_id(self, user_id=0, convert_to_object=True):
		return self._db_provider().get_user_profile_by_user_id(user_id=user_id, convert_to_object=convert_to_object)

	def get_players_who_played_during_time_range(self, min_timestamp='1900-01-01 00:00:00', max_timestamp='2100-01-01 00:00:00'):
		return self._db_provider().get_players_who_played_during_time_range(min_timestamp=min_timestamp, max_timestamp=max_timestamp)

	def get_unlocked_avatars_by_user_id(self, user_id, convert_to_object=True):
		return self._db_provider().get_unlocked_avatars_by_user_id(user_id=user_id, convert_to_object=convert_to_object)

	def get_unlocked_avatars_for_server(self, convert_to_object=True):
		return self._db_provider().get_unlocked_avatars_for_server(convert_to_object=convert_to_object)

	def has_user_unlocked_avatar(self, user_id=0, avatar_id=0):
		return self._db_provider().has_user_unlocked_avatar(user_id=user_id, avatar_id=avatar_id)

	def batch_check_unlocked_avatars(self, avatar_ids, user_id):
		return self._db_provider().batch_check_unlocked_avatars(avatar_ids=avatar_ids, user_id=user_id)

	def get_inventory_item_by_user_id_and_item_id(self, user_id=0, item_id=0, item_quantity=0, convert_to_object=True):
		return self._db_provider().get_inventory_item_by_user_id_and_item_id(
			user_id=user_id,
			item_id=item_id,
			item_quantity=item_quantity,
			convert_to_object=convert_to_object,
		)

	def get_inventory_item_collection_by_user_id(self, user_id=0, convert_to_object=True):
		return self._db_provider().get_inventory_item_collection_by_user_id(user_id=user_id, convert_to_object=convert_to_object)

	def get_player_trap_link_by_user_id(self, user_id=0, convert_to_object=True):
		return self._db_provider().get_player_trap_link_by_user_id(user_id=user_id, convert_to_object=convert_to_object)

	def get_player_trap_link_by_item_id(self, user_id=0, item_id=0, convert_to_object=True):
		return self._db_provider().get_player_trap_link_by_item_id(user_id=user_id, item_id=item_id, convert_to_object=convert_to_object)

	def get_player_trap_links_for_server(self, convert_to_object=True):
		return self._db_provider().get_player_trap_links_for_server(convert_to_object=convert_to_object)


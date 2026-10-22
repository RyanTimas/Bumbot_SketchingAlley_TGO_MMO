from src.caching.db_specific_caches.creature_cache import CreatureCache
from src.caching.db_specific_caches.environment_cache import EnvironmentCache
from src.caching.db_specific_caches.quest_collection_cache import QuestCollectionCache


class ReferenceLookupCache:
    """Compatibility facade that routes legacy calls to split domain caches."""

    def __init__(self, creature_cache: CreatureCache, environment_cache: EnvironmentCache, quest_collection_cache: QuestCollectionCache):
        self._creature_cache = creature_cache
        self._environment_cache = environment_cache
        self._quest_collection_cache = quest_collection_cache

    def get_all_creatures(self, convert_to_object=True):
        return self._creature_cache.get_all_creatures(convert_to_object=convert_to_object)

    def get_creature_by_creature_id(self, creature_id=-1, convert_to_object=True):
        return self._creature_cache.get_creature_by_creature_id(creature_id=creature_id, convert_to_object=convert_to_object)

    def get_creature_by_dex_and_variant_no(self, dex_no=0, variant_no=1, convert_to_object=True):
        return self._creature_cache.get_creature_by_dex_and_variant_no(dex_no=dex_no, variant_no=variant_no, convert_to_object=convert_to_object)

    def get_environment_by_id(self, environment_id=-1, convert_to_object=True):
        return self._environment_cache.get_environment_by_id(environment_id=environment_id, convert_to_object=convert_to_object)

    def get_environments_by_dex_no(self, dex_no=0, convert_to_object=True):
        return self._environment_cache.get_environments_by_dex_no(dex_no=dex_no, convert_to_object=convert_to_object)

    def get_environment_by_dex_no_and_variant_no(self, dex_no=0, variant_no=0, convert_to_object=True):
        return self._environment_cache.get_environment_by_dex_no_and_variant_no(dex_no=dex_no, variant_no=variant_no, convert_to_object=convert_to_object)

    def get_all_environments_in_rotation(self, convert_to_object=True):
        return self._environment_cache.get_all_environments_in_rotation(convert_to_object=convert_to_object)

    def get_all_environments_in_rotation_by_time(self, is_day_night=1, convert_to_object=True):
        return self._environment_cache.get_all_environments_in_rotation_by_time(is_day_night=is_day_night, convert_to_object=convert_to_object)

    def get_collection_by_collection_id(self, convert_to_object=False):
        return self._quest_collection_cache.get_collection_by_collection_id(convert_to_object=convert_to_object)

    def get_active_collections(self, convert_to_object=False):
        return self._quest_collection_cache.get_active_collections(convert_to_object=convert_to_object)

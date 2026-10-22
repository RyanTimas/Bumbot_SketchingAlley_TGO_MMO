from collections import defaultdict
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from src.caching.cache_base import CacheLoadStrategy, StaticContentCacheBase
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature


@dataclass(frozen=True, slots=True)
class CreatureCacheSnapshot:
    """Immutable snapshot for stable creature and environment-creature lookups."""

    all_creatures: Tuple[TGOCreature, ...]
    creatures_by_id: Mapping[int, TGOCreature]
    creatures_by_dex_and_variant: Mapping[tuple[int, int], TGOCreature]

    all_environment_creatures: Tuple[TGOCreature, ...]
    environment_creatures_by_environment_id: Mapping[int, Tuple[TGOCreature, ...]]


class CreatureCache(StaticContentCacheBase[CreatureCacheSnapshot]):
    """Cache for creature, environment-creature, and user-creature access wrappers."""

    def __init__(self, db_provider=None, logger=None, load_strategy: CacheLoadStrategy = CacheLoadStrategy.EAGER):
        super().__init__(load_strategy=load_strategy, logger=logger)
        self._db_provider = db_provider or get_tgommo_db_handler

    def _load_snapshot(self) -> CreatureCacheSnapshot:
        db = self._db_provider()

        all_creatures = db.get_all_creatures(convert_to_object=True) or []
        all_environment_creatures = db.get_all_environment_creatures(convert_to_object=True) or []

        environment_creatures_by_environment_id: dict[int, list[TGOCreature]] = defaultdict(list)
        seen_by_environment_id: dict[int, set[tuple[int, int, int, int]]] = defaultdict(set)
        for creature in all_environment_creatures:
            dedupe_key = (creature.creature_id, creature.variant_no, creature.local_dex_no, creature.local_variant_no)
            if dedupe_key in seen_by_environment_id[creature.environment_id]:
                continue
            seen_by_environment_id[creature.environment_id].add(dedupe_key)
            environment_creatures_by_environment_id[creature.environment_id].append(creature)

        return CreatureCacheSnapshot(
            all_creatures=tuple(all_creatures),
            creatures_by_id=MappingProxyType({creature.creature_id: creature for creature in all_creatures}),
            creatures_by_dex_and_variant=MappingProxyType({(creature.dex_no, creature.variant_no): creature for creature in all_creatures}),
            all_environment_creatures=tuple(all_environment_creatures),
            environment_creatures_by_environment_id=MappingProxyType({key: tuple(value) for key, value in environment_creatures_by_environment_id.items()}),
        )

    # Creature wrappers
    def get_all_creatures(self, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_all_creatures(convert_to_object=False)
        return list(self.snapshot.all_creatures)

    def get_creature_by_creature_id(self, creature_id=-1, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_creature_by_creature_id(creature_id=creature_id, convert_to_object=False)

        cached = self.snapshot.creatures_by_id.get(creature_id)
        if cached is not None:
            return cached
        return self._db_provider().get_creature_by_creature_id(creature_id=creature_id, convert_to_object=True)

    def get_creature_by_dex_and_variant_no(self, dex_no=0, variant_no=1, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_creature_by_dex_and_variant_no(dex_no=dex_no, variant_no=variant_no, convert_to_object=False)

        cached = self.snapshot.creatures_by_dex_and_variant.get((dex_no, variant_no))
        if cached is not None:
            return cached
        return self._db_provider().get_creature_by_dex_and_variant_no(dex_no=dex_no, variant_no=variant_no, convert_to_object=True)

    # Environment creature wrappers
    def get_all_environment_creatures(self, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_all_environment_creatures(convert_to_object=False)
        return list(self.snapshot.all_environment_creatures)

    def get_creatures_for_environment_by_environment_id(self, environment_id=-1, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_creatures_for_environment_by_environment_id(environment_id=environment_id, convert_to_object=False)

        cached = self.snapshot.environment_creatures_by_environment_id.get(environment_id)
        if cached is not None:
            return list(cached)
        return self._db_provider().get_creatures_for_environment_by_environment_id(environment_id=environment_id, convert_to_object=True)

    def get_environment_creature_by_environment_id_and_creature_id(self, environment_id=-1, creature_id=-1, convert_to_object=True):
        return self._db_provider().get_environment_creature_by_environment_id_and_creature_id(
            environment_id=environment_id,
            creature_id=creature_id,
            convert_to_object=convert_to_object,
        )

    def get_environment_creature_by_environment_dex_no_and_creature_id(self, environment_dex_no=-1, creature_id=-1, convert_to_object=True):
        return self._db_provider().get_environment_creature_by_environment_dex_no_and_creature_id(
            environment_dex_no=environment_dex_no,
            creature_id=creature_id,
            convert_to_object=convert_to_object,
        )

    def get_creatures_for_environment_by_dex_no(self, dex_no=0, exclude_duplicates=False, convert_to_object=True):
        return self._db_provider().get_creatures_for_environment_by_dex_no(
            dex_no=dex_no,
            exclude_duplicates=exclude_duplicates,
            convert_to_object=convert_to_object,
        )

    # User creature wrappers (kept pass-through for live user-state correctness)
    def get_user_creature_by_catch_id(self, catch_id=0, convert_to_object=True):
        return self._db_provider().get_user_creature_by_catch_id(catch_id=catch_id, convert_to_object=convert_to_object)

    def get_user_creatures_by_catch_ids(self, catch_ids, convert_to_object=True):
        return self._db_provider().get_user_creatures_by_catch_ids(catch_ids=catch_ids, convert_to_object=convert_to_object)

    def get_user_creatures_by_dex_no(self, dex_no=0, convert_to_object=True):
        return self._db_provider().get_user_creatures_by_dex_no(dex_no=dex_no, convert_to_object=convert_to_object)

    def get_user_creatures_by_dex_no_and_variant_no(self, dex_no=0, variant_no=0, convert_to_object=True):
        return self._db_provider().get_user_creatures_by_dex_no_and_variant_no(dex_no=dex_no, variant_no=variant_no, convert_to_object=convert_to_object)

    def get_user_creatures_by_creature_id(self, creature_id=0, convert_to_object=True):
        return self._db_provider().get_user_creatures_by_creature_id(creature_id=creature_id, convert_to_object=convert_to_object)

    def get_user_creatures_by_user_id(self, user_id=0, is_released=False, convert_to_object=True):
        return self._db_provider().get_user_creatures_by_user_id(user_id=user_id, is_released=is_released, convert_to_object=convert_to_object)

    def get_user_creatures_by_user_id_and_dex_no(self, user_id=0, dex_no=0, convert_to_object=True):
        return self._db_provider().get_user_creatures_by_user_id_and_dex_no(user_id=user_id, dex_no=dex_no, convert_to_object=convert_to_object)

    def get_user_creatures_by_user_id_and_dex_no_and_variant_no(self, user_id=0, dex_no=0, variant_no=0, convert_to_object=True):
        return self._db_provider().get_user_creatures_by_user_id_and_dex_no_and_variant_no(
            user_id=user_id,
            dex_no=dex_no,
            variant_no=variant_no,
            convert_to_object=convert_to_object,
        )

    def get_mythical_user_creatures_by_user_id_and_dex_no(self, user_id=0, dex_no=0, convert_to_object=True):
        return self._db_provider().get_mythical_user_creatures_by_user_id_and_dex_no(user_id=user_id, dex_no=dex_no, convert_to_object=convert_to_object)

    def get_mythical_user_creatures_by_user_id_and_dex_no_and_variant_no(self, user_id=0, dex_no=0, variant_no=1, convert_to_object=True):
        return self._db_provider().get_mythical_user_creatures_by_user_id_and_dex_no_and_variant_no(
            user_id=user_id,
            dex_no=dex_no,
            variant_no=variant_no,
            convert_to_object=convert_to_object,
        )

    def get_afk_user_creatures_by_user_id(self, user_id=0, convert_to_object=True):
        return self._db_provider().get_afk_user_creatures_by_user_id(user_id=user_id, convert_to_object=convert_to_object)


from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from src.caching.cache_base import CacheLoadStrategy, StaticContentCacheBase
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOEnvironment import TGOEnvironment


@dataclass(frozen=True, slots=True)
class EnvironmentCacheSnapshot:
    """Immutable snapshot for environment lookups in active rotation."""

    environments_in_rotation: Tuple[TGOEnvironment, ...]
    environments_by_time: Mapping[int, Tuple[TGOEnvironment, ...]]
    environments_by_id: Mapping[int, TGOEnvironment]
    environments_by_dex_no: Mapping[int, Tuple[TGOEnvironment, ...]]
    environments_by_dex_and_variant: Mapping[tuple[int, int], TGOEnvironment]


class EnvironmentCache(StaticContentCacheBase[EnvironmentCacheSnapshot]):
    """Cache wrapper for environment queries."""

    def __init__(self, db_provider=None, logger=None, load_strategy: CacheLoadStrategy = CacheLoadStrategy.EAGER):
        super().__init__(load_strategy=load_strategy, logger=logger)
        self._db_provider = db_provider or get_tgommo_db_handler

    def _load_snapshot(self) -> EnvironmentCacheSnapshot:
        db = self._db_provider()

        day_environments = db.get_all_environments_in_rotation_by_time(is_day_night=0, convert_to_object=True) or []
        night_environments = db.get_all_environments_in_rotation_by_time(is_day_night=1, convert_to_object=True) or []
        environments_in_rotation = day_environments + night_environments

        environments_by_id = {environment.environment_id: environment for environment in environments_in_rotation}
        environments_by_dex_no: dict[int, list[TGOEnvironment]] = {}
        environments_by_dex_and_variant = {}
        for environment in environments_in_rotation:
            environments_by_dex_no.setdefault(environment.dex_no, []).append(environment)
            environments_by_dex_and_variant[(environment.dex_no, environment.variant_no)] = environment

        return EnvironmentCacheSnapshot(
            environments_in_rotation=tuple(environments_in_rotation),
            environments_by_time=MappingProxyType({0: tuple(day_environments), 1: tuple(night_environments)}),
            environments_by_id=MappingProxyType(environments_by_id),
            environments_by_dex_no=MappingProxyType({key: tuple(value) for key, value in environments_by_dex_no.items()}),
            environments_by_dex_and_variant=MappingProxyType(environments_by_dex_and_variant),
        )

    def get_environment_by_id(self, environment_id=-1, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_environment_by_id(environment_id=environment_id, convert_to_object=False)

        cached = self.snapshot.environments_by_id.get(environment_id)
        if cached is not None:
            return cached
        return self._db_provider().get_environment_by_id(environment_id=environment_id, convert_to_object=True)

    def get_environments_by_dex_no(self, dex_no=0, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_environments_by_dex_no(dex_no=dex_no, convert_to_object=False)

        cached = self.snapshot.environments_by_dex_no.get(dex_no)
        if cached is not None:
            return list(cached)
        return self._db_provider().get_environments_by_dex_no(dex_no=dex_no, convert_to_object=True)

    def get_environment_by_dex_no_and_variant_no(self, dex_no=0, variant_no=0, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_environment_by_dex_no_and_variant_no(dex_no=dex_no, variant_no=variant_no, convert_to_object=False)

        lookup_variant = variant_no if variant_no != 0 else 1
        cached = self.snapshot.environments_by_dex_and_variant.get((dex_no, lookup_variant))
        if cached is not None:
            return cached
        return self._db_provider().get_environment_by_dex_no_and_variant_no(dex_no=dex_no, variant_no=variant_no, convert_to_object=True)

    def get_all_environments_in_rotation(self, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_all_environments_in_rotation(convert_to_object=False)
        return list(self.snapshot.environments_in_rotation)

    def get_all_environments_in_rotation_by_time(self, is_day_night=1, convert_to_object=True):
        if not convert_to_object:
            return self._db_provider().get_all_environments_in_rotation_by_time(is_day_night=is_day_night, convert_to_object=False)

        cached = self.snapshot.environments_by_time.get(is_day_night)
        if cached is not None:
            return list(cached)
        return self._db_provider().get_all_environments_in_rotation_by_time(is_day_night=is_day_night, convert_to_object=True)

    def get_random_environment_in_rotation(self, is_night_environment=None, convert_to_object=False):
        return self._db_provider().get_random_environment_in_rotation(
            is_night_environment=is_night_environment,
            convert_to_object=convert_to_object,
        )


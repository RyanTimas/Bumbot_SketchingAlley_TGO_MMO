from collections import defaultdict
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, FrozenSet, Mapping, Optional, Protocol, Tuple, cast

from src.caching.cache_base import CacheLoadStrategy, StaticContentCacheBase, TSnapshot
from src.commons.CommonDecorators import measure_execution_time
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import BOTH, DAY, NIGHT


@dataclass(frozen=True, slots=True)
class EnvironmentCreatureCacheSnapshot:
    """Immutable snapshot for environment creature lookups."""

    all_environment_creatures: Tuple[TGOCreature, ...]
    creatures_by_environment_and_spawn: Mapping[Tuple[int, str], Tuple[TGOCreature, ...]]
    creatures_by_environment: Mapping[int, Tuple[TGOCreature, ...]]
    creatures_by_id: Mapping[int, TGOCreature]
    spawn_membership: FrozenSet[Tuple[int, int, str]]


class EnvironmentCreatureCache(StaticContentCacheBase[EnvironmentCreatureCacheSnapshot]):
    """Static-content cache for environment creature lookups.

    Load strategy is configurable so the same base class can be reused for lazy
    or hybrid caches later. For this proof-of-concept the cache is registered as
    eager and warmed at startup.
    """

    def __init__(self, db_provider = None, logger=None, load_strategy: CacheLoadStrategy = CacheLoadStrategy.EAGER):
        super().__init__(load_strategy=load_strategy, logger=logger)
        self._db_provider = db_provider or get_tgommo_db_handler()

    def _load_snapshot(self) -> EnvironmentCreatureCacheSnapshot:
        base_creatures = self._db_provider().get_all_creatures() or []
        # Always use the raw DB query path here to avoid cache recursion.
        environment_creatures = self._db_provider().get_all_environment_creatures() or []
        environments_in_rotation = self._db_provider().get_all_environments_in_rotation() or []

        environments_by_id = {environment.environment_id: environment for environment in environments_in_rotation}

        #todo: make this work below
        #environments_by_dex_no = {environment.dex_no: environment for environment in environments_in_rotation}

        creatures_by_id = {creature.creature_id: creature for creature in base_creatures}
        creatures_by_environment_and_spawn: dict[Tuple[int, str], list[TGOCreature]] = defaultdict(list)
        creatures_by_environment: dict[int, list[TGOCreature]] = defaultdict(list)
        seen_by_environment: dict[int, set[Tuple[int, int, int, int]]] = defaultdict(set)
        spawn_membership: set[Tuple[int, int, str]] = set()

        for creature in environment_creatures:
            environment = environments_by_id.get(creature.environment_id)
            if environment is None:
                continue

            spawn_time = NIGHT if environment.is_night_environment else DAY
            environment_dex_no = environment.dex_no
            dedupe_key = (creature.creature_id, creature.variant_no, creature.local_dex_no, creature.local_variant_no)

            creatures_by_environment_and_spawn[(environment_dex_no, spawn_time)].append(creature)
            spawn_membership.add((creature.creature_id, environment_dex_no, spawn_time))

            if dedupe_key not in seen_by_environment[environment_dex_no]:
                creatures_by_environment[environment_dex_no].append(creature)
                seen_by_environment[environment_dex_no].add(dedupe_key)

        return EnvironmentCreatureCacheSnapshot(
            all_environment_creatures=tuple(environment_creatures),
            creatures_by_environment_and_spawn=MappingProxyType({key: tuple(value) for key, value in creatures_by_environment_and_spawn.items()}),
            creatures_by_environment=MappingProxyType({key: tuple(value) for key, value in creatures_by_environment.items()}),
            creatures_by_id=MappingProxyType(creatures_by_id),
            spawn_membership=frozenset(spawn_membership),
        )

    @staticmethod
    def _resolve_environment_dex_no(environment: int | TGOEnvironment) -> int:
        return environment.dex_no if isinstance(environment, TGOEnvironment) else int(environment)

    def get_creatures(self, environment: int | TGOEnvironment, spawn_time: str = DAY) -> tuple[TGOCreature, ...]:
        """Return creatures for the requested environment/spawn-time bucket."""
        snapshot = self.snapshot
        environment_dex_no = self._resolve_environment_dex_no(environment)

        if spawn_time == BOTH:
            day_bucket = snapshot.creatures_by_environment_and_spawn.get((environment_dex_no, DAY), ())
            night_bucket = snapshot.creatures_by_environment_and_spawn.get((environment_dex_no, NIGHT), ())
            seen: set[tuple[int, int, int, int]] = set()
            merged: list[TGOCreature] = []
            for creature in (*day_bucket, *night_bucket):
                key = (creature.creature_id, creature.variant_no, creature.local_dex_no, creature.local_variant_no)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(creature)
            return tuple(merged)

        return snapshot.creatures_by_environment_and_spawn.get((environment_dex_no, spawn_time), ())

    def get_all_creatures_for_environment(self, environment_id: int | TGOEnvironment) -> tuple[TGOCreature, ...]:
        """Return a deduplicated list of creatures that can appear in an environment."""
        snapshot = self.snapshot
        environment_dex_no = self._resolve_environment_dex_no(environment_id)
        return snapshot.creatures_by_environment.get(environment_dex_no, ())

    def get_all_environment_creatures(self) -> tuple[TGOCreature, ...]:
        """Return all environment-creature rows in canonical DB order."""
        return self.snapshot.all_environment_creatures

    def get_creature_by_id(self, creature_id: int) -> Optional[TGOCreature]:
        """Return the canonical creature record for a creature ID."""
        return self.snapshot.creatures_by_id.get(creature_id)

    def can_creature_spawn(self, creature_id: int, environment: int | TGOEnvironment, spawn_time: str) -> bool:
        """Return whether a creature can spawn in the requested environment bucket."""
        snapshot = self.snapshot
        environment_dex_no = self._resolve_environment_dex_no(environment)
        return (creature_id, environment_dex_no, spawn_time) in snapshot.spawn_membership



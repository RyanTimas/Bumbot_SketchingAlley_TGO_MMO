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

    all_creatures: Tuple[TGOCreature, ...]
    all_environment_creatures: Tuple[TGOCreature, ...]

    all_creatures_by_id: Mapping[int, TGOCreature]

    all_environment_creatures_by_environment_dex_no: Mapping[int, Tuple[TGOCreature, ...]]
    all_environment_creatures_by_environment_id: Mapping[int, Tuple[TGOCreature, ...]]

    spawn_membership: FrozenSet[Tuple[int, int, str]]


class EnvironmentCreatureCache(StaticContentCacheBase[EnvironmentCreatureCacheSnapshot]):
    """Static-content cache for environment creature lookups."""
    def __init__(self, db_provider = None, logger=None, load_strategy: CacheLoadStrategy = CacheLoadStrategy.EAGER):
        super().__init__(load_strategy=load_strategy, logger=logger)
        self._db_provider = db_provider or get_tgommo_db_handler()

    def _load_snapshot(self) -> EnvironmentCreatureCacheSnapshot:
        # GRAB ALL DATA FROM THE DATABASE
        base_creatures = self._db_provider().get_all_creatures() or []
        environment_creatures = self._db_provider().get_all_environment_creatures() or []

        environments_by_id = {environment.environment_id: environment for environment in self._db_provider().get_all_environments_in_rotation() or []}
        environments_by_dex_no = self._build_environments_by_dex_no(environments_by_id)

        # PLACE CREATURES INTO  LOOKUP ENVIRONMENTS

        # build a mapping of environment dex_no to environment for quick lookups
        creatures_by_id = {creature.creature_id: creature for creature in base_creatures}
        creatures_by_environment_and_spawn: dict[Tuple[int, str], list[TGOCreature]] = defaultdict(list)
        creatures_by_environment: dict[int, list[TGOCreature]] = defaultdict(list)
        seen_by_environment: dict[int, set[Tuple[int, int, int, int]]] = defaultdict(set)
        spawn_membership: set[Tuple[int, int, str]] = set()

        creatures_by_environment_id = self._build_creatures_by_environment_id(environment_creatures=environment_creatures)

        for creature in environment_creatures:
            environment = environments_by_id.get(creature.environment_id)
            if environment is None:
                continue

            spawn_time = NIGHT if environment.is_night_environment else DAY
            environment_dex_no = environment.dex_no
            spawn_membership.add((creature.creature_id, environment_dex_no, spawn_time))

        return EnvironmentCreatureCacheSnapshot(
            all_creatures=tuple(base_creatures),
            all_environment_creatures=tuple(environment_creatures),
            all_environment_creatures_by_environment_dex_no=MappingProxyType({key: tuple(value) for key, value in self._build_creatures_by_environment_dex_no(environment_creatures=environment_creatures, environments_by_dex_no=environments_by_dex_no,).items()}),
            all_environment_creatures_by_environment_id=MappingProxyType({key: tuple(value) for key, value in creatures_by_environment_id.items()}),
            all_creatures_by_id=MappingProxyType(creatures_by_id),
            spawn_membership=frozenset(spawn_membership),
        )

    '''---- CACHE BUILDING FUNCTIONS ------------------------------------------------------------------------------------------------------------------------'''
    @staticmethod
    def _build_environments_by_dex_no(environments_by_id)-> dict[int, list[TGOEnvironment]]:
        """Return a mapping of environment dex_no to environment."""
        environments_by_dex_no: dict[int, list[TGOEnvironment]] = defaultdict(list)
        for environment in environments_by_id.values():
            environments_by_dex_no[environment.dex_no].append(environment)
        return environments_by_dex_no

    @staticmethod
    def _build_creatures_by_environment_dex_no(environment_creatures: list[TGOCreature], environments_by_dex_no: dict[int, list[TGOEnvironment]],) -> dict[int, list[TGOCreature]]:
        """Return a mapping of environment dex_no to deduplicated creatures."""
        creatures_by_environment_dex_no: dict[int, list[TGOCreature]] = defaultdict(list)
        environment_id_to_dex_no = {environment.environment_id: dex_no for dex_no, environments in environments_by_dex_no.items() for environment in environments}
        seen_by_dex_no: dict[int, set[tuple[int, int, int, int]]] = defaultdict(set)

        for creature in environment_creatures:
            environment_dex_no = environment_id_to_dex_no.get(creature.environment_id)
            if environment_dex_no is None:
                continue

            dedupe_key = (creature.creature_id, creature.variant_no, creature.local_dex_no, creature.local_variant_no)
            if dedupe_key in seen_by_dex_no[environment_dex_no]:
                continue

            creatures_by_environment_dex_no[environment_dex_no].append(creature)
            seen_by_dex_no[environment_dex_no].add(dedupe_key)
        return creatures_by_environment_dex_no

    @staticmethod
    def _build_creatures_by_environment_id(environment_creatures: list[TGOCreature]) -> dict[int, list[TGOCreature]]:
        """Return a mapping of environment_id to deduplicated creatures."""
        creatures_by_environment_id: dict[int, list[TGOCreature]] = defaultdict(list)
        seen_by_environment_id: dict[int, set[tuple[int, int, int, int]]] = defaultdict(set)

        for creature in environment_creatures:
            dedupe_key = (creature.creature_id, creature.variant_no, creature.local_dex_no, creature.local_variant_no)
            if dedupe_key in seen_by_environment_id[creature.environment_id]:
                continue

            creatures_by_environment_id[creature.environment_id].append(creature)
            seen_by_environment_id[creature.environment_id].add(dedupe_key)

        return creatures_by_environment_id


    @staticmethod
    def _resolve_environment_dex_no(environment: int | TGOEnvironment) -> int:
        return environment.dex_no if isinstance(environment, TGOEnvironment) else int(environment)


    '''---- GETTERS FOR RETRIEVING CACHED DATA ------------------------------------------------------------------------------------------------------------------------'''
    def get_creatures(self, environment: int | TGOEnvironment, spawn_time: str = DAY) -> tuple[TGOCreature, ...]:
        """Return creatures for the requested environment/spawn-time bucket."""
        snapshot = self.snapshot
        environment_dex_no = self._resolve_environment_dex_no(environment)

        matching_creatures = [
            creature
            for creature in snapshot.all_environment_creatures
            if (creature.creature_id, environment_dex_no, spawn_time) in snapshot.spawn_membership
        ]

        if spawn_time == BOTH:
            merged: list[TGOCreature] = []
            seen: set[tuple[int, int, int, int]] = set()
            for creature in matching_creatures:
                key = (creature.creature_id, creature.variant_no, creature.local_dex_no, creature.local_variant_no)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(creature)
            return tuple(merged)

        return tuple(matching_creatures)

    def get_all_creatures_for_environment(self, environment_id: int | TGOEnvironment) -> tuple[TGOCreature, ...]:
        """Return a deduplicated list of creatures that can appear in an environment."""
        environment_dex_no = self._resolve_environment_dex_no(environment_id)
        return self.snapshot.all_environment_creatures_by_environment_dex_no.get(environment_dex_no, ())

    def get_environment_creature_by_environment_dex_no_and_creature_id(self, environment_dex_no: int, creature_id: int) -> Optional[TGOCreature]:
        """Return the canonical creature record for a creature ID in a specific environment dex_no."""
        for creature in self.snapshot.all_environment_creatures_by_environment_dex_no.get(environment_dex_no, ()):
            if creature.creature_id == creature_id:
                return creature
        return None

    def get_all_environment_creatures(self) -> tuple[TGOCreature, ...]:
        """Return all environment-creature rows in canonical DB order."""
        return self.snapshot.all_environment_creatures

    def get_creature_by_id(self, creature_id: int) -> Optional[TGOCreature]:
        """Return the canonical creature record for a creature ID."""
        return self.snapshot.all_creatures_by_id.get(creature_id)

    def can_creature_spawn(self, creature_id: int, environment: int | TGOEnvironment, spawn_time: str) -> bool:
        """Return whether a creature can spawn in the requested environment bucket."""
        snapshot = self.snapshot
        environment_dex_no = self._resolve_environment_dex_no(environment)
        return (creature_id, environment_dex_no, spawn_time) in snapshot.spawn_membership



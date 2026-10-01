import threading
import time
import asyncio
from typing import Callable, Dict, Any, List, Optional, Set


def _default_db_provider():
    """
    Try to import a project DB provider helper. If not available,
    callers must pass a `db_provider` callable to ReferenceData.
    """
    try:
        # adapt this import to your project if you have a global getter
        from src.db.DBHandler import get_tgommo_db_handler  # type: ignore
        return get_tgommo_db_handler
    except Exception:
        # fallback: indicate no default provider available
        return None


class DatabaseCacheHandler:
    """
    Singleton service that centralizes DB calls and caches common reference objects:
    - environment creature maps (keyed by environment dex_no)
    - global item list

    Usage:
      from src.services.reference_data import ReferenceData
      ref = ReferenceData.get_instance(db_provider=get_tgommo_db_handler)
      creatures = ref.get_environment_creatures(environment_dex_no=123)
      items = ref.get_item_list()

    Notes:
      - Thread\-safe.
      - Cached entries have optional TTL (seconds). Set ttl_seconds=None to never expire.
      - Call `refresh_all()` or `await async_refresh_all()` to force reload.
    """
    _instance = None
    _instance_lock = threading.Lock()

    @classmethod
    def get_instance(cls, db_provider: Optional[Callable[[], Any]] = None, ttl_seconds: Optional[int] = 300):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls(db_provider=db_provider, ttl_seconds=ttl_seconds)
            elif db_provider is not None:
                # allow providing provider at first retrieval
                cls._instance._db_provider = db_provider
            return cls._instance

    def __init__(self, db_provider: Optional[Callable[[], Any]] = None, ttl_seconds: Optional[int] = 300):
        self._db_provider = db_provider or _default_db_provider()
        self._ttl_seconds = ttl_seconds

        self._lock = threading.RLock()
        # caches
        self._environment_creature_map: Dict[int, Dict[str, Any]] = {}
        # map: env_dex_no -> {"loaded_at": ts, "creatures": [...]}
        self._item_list_cache: Dict[str, Any] = {"loaded_at": 0, "items": []}

    # --- internal helpers ---

    def _now(self) -> float:
        return time.time()

    def _is_expired(self, loaded_at: float) -> bool:
        if self._ttl_seconds is None:
            return False
        return (self._now() - loaded_at) > self._ttl_seconds

    def _get_db(self):
        if callable(self._db_provider):
            return self._db_provider()
        raise RuntimeError("No DB provider available. Pass `db_provider` to ReferenceData.get_instance(...)")

    def _try_calls(self, db, candidate_names: List[str], *args, **kwargs):
        """
        Try a list of method names on the DB handler and return the first non-empty usable result.
        """
        for name in candidate_names:
            fn = getattr(db, name, None)
            if not callable(fn):
                continue
            try:
                res = fn(*args, **kwargs)
            except Exception:
                continue
            # prefer iterable / mapping results over integers/None
            if res is None:
                continue
            return res
        return None

    # --- environment creature map access ---

    def get_environment_creatures(self, environment_dex_no: int) -> List[Any]:
        """
        Return cached list of creatures for the given environment dex number.
        Loads from DB on first access or when cache expired.
        """
        with self._lock:
            entry = self._environment_creature_map.get(environment_dex_no)
            if entry and not self._is_expired(entry.get("loaded_at", 0)):
                return entry["creatures"]

        # load outside of the lock to avoid long blocking, but replace under lock
        creatures = self._load_environment_creatures(environment_dex_no)

        with self._lock:
            self._environment_creature_map[environment_dex_no] = {"loaded_at": self._now(), "creatures": creatures}
        return creatures

    def _load_environment_creatures(self, environment_dex_no: int) -> List[Any]:
        db = self._get_db()
        # candidate method names used in the project (update as needed)
        candidates = [
            "get_creatures_for_environment_by_dex_no",
            "get_creatures_for_environment",
            "get_creatures_for_environment_dex_no",
        ]
        res = self._try_calls(db, candidates, dex_no=environment_dex_no)
        if res is None:
            # final attempt: call with other param names
            res = self._try_calls(db, ["get_creatures_for_environment_by_dex_no"], environment_dex_no)
        # Normalise to list
        if res is None:
            return []
        if isinstance(res, (list, tuple)):
            return list(res)
        # If returned a mapping or set, convert to list
        try:
            return list(res)
        except Exception:
            return []

    def refresh_environment(self, environment_dex_no: int) -> List[Any]:
        """
        Force reload for one environment and replace cache.
        """
        creatures = self._load_environment_creatures(environment_dex_no)
        with self._lock:
            self._environment_creature_map[environment_dex_no] = {"loaded_at": self._now(), "creatures": creatures}
        return creatures

    # --- item list access ---

    def get_item_list(self) -> List[Any]:
        """
        Return cached global item list.
        """
        with self._lock:
            if not self._is_expired(self._item_list_cache.get("loaded_at", 0)) and self._item_list_cache.get("items"):
                return self._item_list_cache["items"]

        items = self._load_item_list()
        with self._lock:
            self._item_list_cache = {"loaded_at": self._now(), "items": items}
        return items

    def _load_item_list(self) -> List[Any]:
        db = self._get_db()
        candidates = [
            "get_all_items",
            "get_item_list",
            "get_items",
        ]
        res = self._try_calls(db, candidates)
        if res is None:
            return []
        if isinstance(res, (list, tuple)):
            return list(res)
        try:
            return list(res)
        except Exception:
            return []

    def refresh_items(self) -> List[Any]:
        items = self._load_item_list()
        with self._lock:
            self._item_list_cache = {"loaded_at": self._now(), "items": items}
        return items

    # --- global refresh helpers ---

    def refresh_all(self):
        """
        Force reload all cached reference data synchronously.
        """
        with self._lock:
            env_keys: Set[int] = set(self._environment_creature_map.keys())
        # refresh outside lock
        for dex_no in env_keys:
            self.refresh_environment(dex_no)
        self.refresh_items()

    async def async_refresh_all(self):
        """
        Run refresh_all on a background thread so callers from async code won't block.
        """
        return await asyncio.to_thread(self.refresh_all)
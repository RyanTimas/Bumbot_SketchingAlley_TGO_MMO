# python
import random
import threading
from typing import Optional, Tuple, Dict

from src.resources.constants.TGO_MMO_constants import ITEM_ID_TRAP

# Global map storing user_id -> (battery_count, trap_id)
TRAP_BATTERY_MAP: Dict[int, Tuple[int, int]] = {}
_TRAP_MAP_LOCK = threading.Lock()


class TrapHandler:
    """Manage trap batteries using module-level globals and a lock."""

    @staticmethod
    def load_battery(user_id: int, trap_id: Optional[int] = None, charge_count=8) -> int:
        """Add 8 charges for user_id. If exists, increment by 8.
        If creating a new entry, trap_id defaults to ITEM_ID_TRAP unless provided.
        If trap_id is provided and user exists, update their trap id to the provided value.
        Returns new total battery count.
        """
        with _TRAP_MAP_LOCK:
            if user_id in TRAP_BATTERY_MAP:
                battery, current_trap = TRAP_BATTERY_MAP[user_id]
                battery += charge_count
                if trap_id is not None:
                    current_trap = trap_id
                TRAP_BATTERY_MAP[user_id] = (battery, current_trap)
                return battery
            else:
                assigned_trap = trap_id if trap_id is not None else ITEM_ID_TRAP
                TRAP_BATTERY_MAP[user_id] = (charge_count, assigned_trap)
                return charge_count

    @staticmethod
    def pull_random_user() -> Optional[Tuple[int, int, int]]:
        """Randomly select a user with battery > 0, decrement their battery by 1 and return
        (user_id, remaining_battery, trap_id). Returns None if no eligible user exists.
        """
        with _TRAP_MAP_LOCK:
            candidates = [uid for uid, (count, _) in TRAP_BATTERY_MAP.items() if count > 0]
            if candidates:
                user_id = random.choice(candidates)
                battery, trap_id = TRAP_BATTERY_MAP[user_id]
                battery -= 1
                TRAP_BATTERY_MAP[user_id] = (battery, trap_id)
                return user_id, battery, trap_id
            return None, None, None


    @staticmethod
    def switch_trap(user_id: int, new_trap_id: int) -> Optional[int]:
        """Switch the trap id associated with user_id.
        If the user exists, replace their trap id and return the previous trap id.
        If the user does not exist, create an entry with 0 battery and the new_trap_id and return None.
        """
        with _TRAP_MAP_LOCK:
            if user_id in TRAP_BATTERY_MAP:
                battery, old_trap = TRAP_BATTERY_MAP[user_id]
                TRAP_BATTERY_MAP[user_id] = (battery, new_trap_id)
                return old_trap
            else:
                TRAP_BATTERY_MAP[user_id] = (0, new_trap_id)
                return None

    @staticmethod
    def get_trap_id(user_id: int) -> Optional[int]:
        """Return the trap id for a user, or None if the user has no entry."""
        with _TRAP_MAP_LOCK:
            entry = TRAP_BATTERY_MAP.get(user_id)
            return entry[1] if entry is not None else None
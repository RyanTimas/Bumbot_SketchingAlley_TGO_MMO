import json
import os
import tempfile
import threading
from typing import Optional

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects import TGOPlayerItem
# Global instance - initialized as None
game_state_manager = None

def initialize_game_state_manager(state_file_path: str = "resources/constants/game_state.json"):
    global game_state_manager
    game_state_manager = GameStateManager(state_file_path)
    return game_state_manager

def get_game_state_manager() -> 'GameStateManager':
    global game_state_manager
    if game_state_manager is None:
        raise RuntimeError("Game state manager not initialized. Call initialize_game_state_manager() first.")
    return game_state_manager

class GameStateManager:
    def __init__(self, state_file_path: str = "resources/constants/game_state.json"):
        self.state_file_path = state_file_path
        self._lock = threading.RLock()
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        directory = os.path.dirname(self.state_file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def _load_state(self) -> dict:
        try:
            if os.path.exists(self.state_file_path):
                with open(self.state_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading game state: {e}")
        return {}

    def _save_state(self, state: dict):
        """Save the entire state to file atomically (write to temp file then replace)."""
        tmp_path = None
        try:
            directory = os.path.dirname(self.state_file_path) or '.'
            with tempfile.NamedTemporaryFile('w', dir=directory, delete=False, encoding='utf-8') as tf:
                json.dump(state, tf, indent=2)
                tmp_path = tf.name
            os.replace(tmp_path, self.state_file_path)
        except Exception as e:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            print(f"Error saving game state: {e}")


    ''' ----- GETTERS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # ENVIRONMENT GETTERS
    def get_environment_change_date(self) -> Optional[str]:
        state = self._load_state()
        return state.get("environment_change_date")

    def get_current_environment(self) -> Optional[tuple]:
        state = self._load_state()
        env_dex = state.get("environment_dex_no")
        env_variant = state.get("environment_variant_no")
        if env_dex is not None and env_variant is not None:
            return env_dex, env_variant
        return None

    # SHOP GETTERS
    def get_shop_date(self) -> Optional[str]:
        state = self._load_state()
        return state.get("shop_date")

    def get_current_shop_inventory(self):
        return self.get_current_shop_items(), self.get_current_shop_avatars()
    def get_current_shop_items(self):
        state = self._load_state()

        shop_items = []
        for item_id in state.get("current_shop_item_ids"):
            item = get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=item_id)
            if item:
                shop_items.append(item)
        return shop_items
    def get_current_shop_avatars(self):
        state = self._load_state()

        shop_avatars = []
        for avatar_id in state.get("current_shop_avatar_ids"):
            avatar = get_tgommo_db_handler().get_avatar_by_id(avatar_id=avatar_id)
            if avatar:
                shop_avatars.append(avatar)
        return shop_avatars

    def get_shop_level(self) -> int:
        """Return the saved shop level (defaults to 1)."""
        state = self._load_state()
        return state.get("shop_level", 1)
    def get_shop_donation_total(self) -> int:
        """Return the saved shop donation total (defaults to 0)."""
        state = self._load_state()
        return state.get("shop_donation_total", 0)

    # general Bumbot state getters
    def get_shiny_message_count(self) -> int:
        state = self._load_state()
        return state.get("shiny_message_count", 0)

    # SPAWN BONUS GETTERS
    def get_active_spawn_bonuses(self) -> list[TGOPlayerItem]:
        state = self._load_state()
        raw = state.get("active_spawn_bonuses", [])
        bonuses: list[TGOPlayerItem] = []
        for b in raw:
            try:
                active_item = get_tgommo_db_handler().get_inventory_item_by_item_id(item_id=b.get("item_id"))
                if active_item:
                    active_item.despawn_timestamp = int(b.get("despawn_ts"))
                    bonuses.append(active_item)
            except Exception:
                continue
        return bonuses

    ''' ----- SETTERS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # ENVIRONMENT SETTERS
    def set_environment_change_date(self, new_date: str):
        state = self._load_state()
        state["environment_change_date"] = new_date
        self._save_state(state)

    def set_current_environment(self, environment_dex_no: int, environment_variant_no: int):
        state = self._load_state()
        state.update({
            "environment_dex_no": environment_dex_no,
            "environment_variant_no": environment_variant_no
        })
        self._save_state(state)

    # SHOP SETTERS
    def set_shop_date(self, new_date: str):
        state = self._load_state()
        state["shop_date"] = new_date
        self._save_state(state)
    def set_current_shop_inventory(self, item_ids: list, avatar_ids: list):
        state = self._load_state()
        state.update({
            "current_shop_item_ids": item_ids,
            "current_shop_avatar_ids": avatar_ids
        })
        self._save_state(state)

    def set_shop_level(self, new_level: int):
        state = self._load_state()
        state["shop_level"] = new_level
        self._save_state(state)
    def set_shop_donation_total(self, new_total: int):
        """Set and persist the shop donation total."""
        state = self._load_state()
        state["shop_donation_total"] = new_total
        self._save_state(state)

    def set_active_spawn_bonuses(self, bonuses: list):
        """Set and persist the list of active spawn bonuses (list of dicts)."""
        state = self._load_state()
        state["active_spawn_bonuses"] = bonuses
        self._save_state(state)

    # General Bumbot state setters
    def set_shiny_message_count(self, new_count: int):
        state = self._load_state()
        state["shiny_message_count"] = new_count
        self._save_state(state)

    ''' ----- ADDERS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # SPAWN BONUS ADDERS
    def add_active_spawn_bonus(self, item_id: int, despawn_ts: int) -> bool:
        """ Add a bonus entry if one with the same item_id doesn't already exist. """
        with self._lock:
            state = self._load_state()
            active_spawn_bonuses = state.get("active_spawn_bonuses", [])
            if any(b.get("item_id") == item_id for b in active_spawn_bonuses):
                return False
            active_spawn_bonuses.append({"item_id": item_id, "despawn_ts": despawn_ts})
            state["active_spawn_bonuses"] = active_spawn_bonuses
            self._save_state(state)
            return True

    ''' ----- REMOVERS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # SPAWN BONUS REMOVERS
    def remove_active_spawn_bonus(self, item_id: str) -> None:
        """Remove any entries matching item_id and persist."""
        with self._lock:
            state = self._load_state()

            active_spawn_bonuses = state.get("active_spawn_bonuses", [])
            active_spawn_bonuses = [bonus for bonus in active_spawn_bonuses if bonus.get("item_id") != item_id]
            state["active_spawn_bonuses"] = active_spawn_bonuses

            self._save_state(state)
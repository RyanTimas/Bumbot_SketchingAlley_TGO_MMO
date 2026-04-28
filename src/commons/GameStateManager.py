import json
import os
from typing import Optional

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler

# Global instance - initialized as None
game_state_manager = None

def initialize_game_state_manager(state_file_path: str = "resources/constants/game_state.json"):
    """Initialize the global game state manager instance"""
    global game_state_manager
    game_state_manager = GameStateManager(state_file_path)
    return game_state_manager

def get_game_state_manager() -> 'GameStateManager':
    """Get the global game state manager instance"""
    global game_state_manager
    if game_state_manager is None:
        raise RuntimeError("Game state manager not initialized. Call initialize_game_state_manager() first.")
    return game_state_manager

class GameStateManager:
    def __init__(self, state_file_path: str = "resources/constants/game_state.json"):
        self.state_file_path = state_file_path
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        directory = os.path.dirname(self.state_file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def _load_state(self) -> dict:
        try:
            if os.path.exists(self.state_file_path):
                with open(self.state_file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading game state: {e}")
        return {}
    def _save_state(self, state: dict):
        """Save the entire state to file."""
        try:
            with open(self.state_file_path, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving game state: {e}")


    ''' ----- GETTERS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def get_current_environment(self) -> Optional[tuple]:
        state = self._load_state()
        env_dex = state.get("environment_dex_no")
        env_variant = state.get("environment_variant_no")
        if env_dex is not None and env_variant is not None:
            return env_dex, env_variant
        return None

    def get_environment_change_date(self) -> Optional[str]:
        state = self._load_state()
        return state.get("environment_change_date")
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

    # general Bumbot state getters
    def get_shiny_message_count(self) -> int:
        state = self._load_state()
        return state.get("shiny_message_count", 0)

    ''' ----- SETTERS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def set_current_environment(self, environment_dex_no: int, environment_variant_no: int):
        state = self._load_state()
        state.update({
            "environment_dex_no": environment_dex_no,
            "environment_variant_no": environment_variant_no
        })
        self._save_state(state)

    def set_environment_change_date(self, new_date: str):
        state = self._load_state()
        state["environment_change_date"] = new_date
        self._save_state(state)
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


    # General Bumbot state setters
    def set_shiny_message_count(self, new_count: int):
        state = self._load_state()
        state["shiny_message_count"] = new_count
        self._save_state(state)
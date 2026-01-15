import json
import os
from typing import Optional

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

    def save_current_environment(self, environment_dex_no: int, environment_variant_no: int):
        """Save the current environment state to file."""
        state = self._load_state()
        state.update({
            "environment_dex_no": environment_dex_no,
            "environment_variant_no": environment_variant_no
        })
        self._save_state(state)

    def load_current_environment(self) -> Optional[tuple]:
        """Load the current environment state from file."""
        state = self._load_state()
        env_dex = state.get("environment_dex_no")
        env_variant = state.get("environment_variant_no")
        if env_dex is not None and env_variant is not None:
            return env_dex, env_variant
        return None

    def _load_state(self) -> dict:
        """Load the entire state from file."""
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
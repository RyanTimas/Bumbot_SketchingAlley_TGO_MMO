import unittest
from unittest.mock import Mock, patch

from src.database.handlers.TGOMMO_DatabaseHandler import TGOMMODatabaseHandler
from src.discord.handlers.CreatureReleaseService import CreatureReleaseService as release_module


class _FakeQueryHandler:
    def __init__(self, profile_row):
        self.profile_row = profile_row
        self.queries = []

    def execute_query(self, query, params=None):
        self.queries.append((query, params))
        if "SELECT player_id" in query:
            return [self.profile_row]
        return []


class CreatureReleaseDisplayCleanupTests(unittest.TestCase):
    def test_clear_released_creatures_preserves_other_display_slots(self):
        handler = TGOMMODatabaseHandler.__new__(TGOMMODatabaseHandler)
        query_handler = _FakeQueryHandler((1, 42, "Player", 1, -1, 101, 202, 303, 404, 505, 606, 0, 3, 1, 0, 1, 0))
        handler.QueryHandler = query_handler
        handler.update_user_profile_display_creature_slots = Mock()

        result = handler.clear_released_creatures_from_display_slots(
            user_id=42,
            creature_ids=[202, 505],
        )

        self.assertTrue(result)
        handler.update_user_profile_display_creature_slots.assert_called_once_with(
            params=(101, -1, 303, 404, -1, 606, 42)
        )

    def test_clear_released_creatures_is_idempotent_when_no_slot_matches(self):
        handler = TGOMMODatabaseHandler.__new__(TGOMMODatabaseHandler)
        query_handler = _FakeQueryHandler((1, 42, "Player", 1, -1, 101, 202, 303, 404, 505, 606, 0, 3, 1, 0, 1, 0))
        handler.QueryHandler = query_handler
        handler.update_user_profile_display_creature_slots = Mock()

        result = handler.clear_released_creatures_from_display_slots(
            user_id=42,
            creature_ids=[999],
        )

        self.assertTrue(result)
        handler.update_user_profile_display_creature_slots.assert_not_called()


class CreatureReleaseServiceTests(unittest.TestCase):
    def test_release_clears_display_slots_before_distributing_rewards(self):
        database_handler = Mock()
        operation_order = []

        def mark_released(*args, **kwargs):
            operation_order.append("release")
            return True

        def clear_display(*args, **kwargs):
            operation_order.append("clear_display")

        database_handler.update_user_creature_set_is_released.side_effect = mark_released
        database_handler.clear_released_creatures_from_display_slots.side_effect = clear_display
        database_handler.get_inventory_item_by_user_id_and_item_id.return_value = Mock(item_quantity=0)
        reward_handler = Mock()

        def get_rewards(*args, **kwargs):
            operation_order.append("rewards")
            return 10, []

        reward_handler.get_release_rewards.side_effect = get_rewards

        with patch.object(release_module, "get_tgommo_db_handler", return_value=database_handler), \
                patch.object(release_module, "CreatureReleaseRewardHandler", return_value=reward_handler):
            result = release_module.CreatureReleaseService._handle_database_operations(
                user_id=42,
                creature_ids=[101, 202],
            )

        self.assertEqual(result, (10, []))
        database_handler.clear_released_creatures_from_display_slots.assert_called_once_with(
            user_id=42,
            creature_ids=[101, 202],
        )
        self.assertEqual(operation_order, ["release", "clear_display", "rewards"])

    def test_failed_release_does_not_clear_display_slots_or_distribute_rewards(self):
        database_handler = Mock()
        database_handler.update_user_creature_set_is_released.return_value = False

        with patch.object(release_module, "get_tgommo_db_handler", return_value=database_handler), \
                patch.object(release_module, "CreatureReleaseRewardHandler") as reward_handler:
            result = release_module.CreatureReleaseService._handle_database_operations(
                user_id=42,
                creature_ids=[101],
            )

        self.assertEqual(result, (None, None))
        database_handler.clear_released_creatures_from_display_slots.assert_not_called()
        reward_handler.assert_not_called()


if __name__ == "__main__":
    unittest.main()


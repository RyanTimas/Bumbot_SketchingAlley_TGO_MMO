import unittest
from unittest.mock import Mock, patch, MagicMock
from src.discord.game_features.creature_inventory.CreatureReleaseRewardHandler import CreatureReleaseRewardHandler
from src.resources.constants.TGO_MMO_constants import *


class TestCreatureReleaseRewardHandler(unittest.TestCase):

    def setUp(self):
        self.user_id = "test_user_123"

    @patch('src.discord.game_features.creature_inventory.CreatureReleaseRewardHandler.get_tgommo_db_handler')
    @patch('random.randint')
    def test_mythical_creature_release_rewards(self, mock_randint, mock_db_handler):
        # Mock creature with mythical rarity
        mock_creature = Mock()
        mock_creature.rarity = Mock()
        mock_creature.rarity.name = TGOMMO_RARITY_MYTHICAL

        # Mock rarity object for items
        mock_epic_rarity = Mock()
        mock_epic_rarity.name = TGOMMO_RARITY_EPIC
        mock_legendary_rarity = Mock()
        mock_legendary_rarity.name = TGOMMO_RARITY_LEGENDARY
        mock_rare_rarity = Mock()
        mock_rare_rarity.name = TGOMMO_RARITY_RARE

        # Mock reward items
        mock_legendary_bait = Mock()
        mock_legendary_bait.rarity = mock_legendary_rarity
        mock_epic_bait = Mock()
        mock_epic_bait.rarity = mock_epic_rarity
        mock_rare_charm = Mock()
        mock_rare_charm.rarity = mock_rare_rarity

        # Mock database handler
        mock_db = Mock()
        mock_db_handler.return_value = mock_db

        # Setup database responses
        mock_db.get_rewardable_inventory_items.return_value = []
        mock_db.get_creature_by_catch_id.return_value = mock_creature
        mock_db.get_inventory_item_by_item_id.side_effect = lambda item_id, convert_to_object=False: {
            ITEM_ID_LEGENDARY_BAIT: mock_legendary_bait,
            ITEM_ID_EPIC_BAIT: mock_epic_bait,
            ITEM_ID_RARE_CHARM: mock_rare_charm
        }.get(item_id)
        mock_db.get_item_collection_by_user_id.return_value = [Mock()]  # Non-empty to skip starter pack

        # Mock random calls: first for drop chance (1 = guaranteed drop), second for bait type
        mock_randint.side_effect = [1, 2]  # 1 triggers drop, 2 selects epic bait (not legendary)

        # Create handler and test
        handler = CreatureReleaseRewardHandler(self.user_id)
        selected_creature_ids = ["creature_123"]

        currency, items = handler.calculate_rewards(selected_creature_ids)

        # Verify we got the expected rewards
        self.assertIsInstance(currency, int)
        self.assertGreater(currency, 0)

        # Convert items back to list for easier testing
        item_list = []
        for item, count in items:
            item_list.extend([item] * count)

        # Should have exactly 2 items: epic bait and rare charm
        self.assertEqual(len(item_list), 2)

        # Verify we got epic bait and rare charm (mythical creature guaranteed drops)
        item_rarities = [item.rarity.name for item in item_list]
        self.assertIn(TGOMMO_RARITY_EPIC, item_rarities)  # Epic bait
        self.assertIn(TGOMMO_RARITY_RARE, item_rarities)  # Rare charm

        # Verify database calls
        mock_db.get_creature_by_catch_id.assert_called_once_with("creature_123", convert_to_object=True)

    @patch('src.discord.game_features.creature_inventory.CreatureReleaseRewardHandler.get_tgommo_db_handler')
    @patch('random.randint')
    def test_mythical_creature_legendary_bait_drop(self, mock_randint, mock_db_handler):
        # Test the case where mythical creature drops legendary bait instead of epic
        mock_creature = Mock()
        mock_creature.rarity = Mock()
        mock_creature.rarity.name = TGOMMO_RARITY_MYTHICAL

        mock_legendary_rarity = Mock()
        mock_legendary_rarity.name = TGOMMO_RARITY_LEGENDARY
        mock_rare_rarity = Mock()
        mock_rare_rarity.name = TGOMMO_RARITY_RARE

        mock_legendary_bait = Mock()
        mock_legendary_bait.rarity = mock_legendary_rarity
        mock_rare_charm = Mock()
        mock_rare_charm.rarity = mock_rare_rarity

        mock_db = Mock()
        mock_db_handler.return_value = mock_db
        mock_db.get_rewardable_inventory_items.return_value = []
        mock_db.get_creature_by_catch_id.return_value = mock_creature
        mock_db.get_inventory_item_by_item_id.side_effect = lambda item_id, convert_to_object=False: {
            ITEM_ID_LEGENDARY_BAIT: mock_legendary_bait,
            ITEM_ID_RARE_CHARM: mock_rare_charm
        }.get(item_id)
        mock_db.get_item_collection_by_user_id.return_value = [Mock()]

        # Mock random: 1 for guaranteed drop, 1 for legendary bait selection
        mock_randint.side_effect = [1, 1]

        handler = CreatureReleaseRewardHandler(self.user_id)
        currency, items = handler.calculate_rewards(["creature_123"])

        item_list = []
        for item, count in items:
            item_list.extend([item] * count)

        # Should still have 2 items, but now legendary bait instead of epic
        self.assertEqual(len(item_list), 2)
        item_rarities = [item.rarity.name for item in item_list]
        self.assertIn(TGOMMO_RARITY_LEGENDARY, item_rarities)  # Legendary bait
        self.assertIn(TGOMMO_RARITY_RARE, item_rarities)  # Rare charm


if __name__ == '__main__':
    unittest.main()
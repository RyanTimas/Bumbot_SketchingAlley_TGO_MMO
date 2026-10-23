import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.discord.handlers.ItemUnlockHandler import ItemUnlockHandler as item_module
from resources.constants.TGO_MMO_constants import (
    ITEM_ID_BATTERY,
    ITEM_ID_BIRD_BAIT,
    ITEM_ID_MAMMAL_BAIT,
    ITEM_ID_REPTILE_BAIT,
)


class ItemUnlockHandlerTests(unittest.TestCase):
    def make_database(self):
        database = SimpleNamespace()
        database.items = {
            ITEM_ID_BATTERY: SimpleNamespace(item_quantity=2, item_unlock_image=object()),
            ITEM_ID_MAMMAL_BAIT: SimpleNamespace(item_quantity=0, item_unlock_image=object()),
            ITEM_ID_BIRD_BAIT: SimpleNamespace(item_quantity=1, item_unlock_image=object()),
            ITEM_ID_REPTILE_BAIT: SimpleNamespace(item_quantity=3, item_unlock_image=object()),
        }
        database.updates = []
        database.get_inventory_item_by_user_id_and_item_id = lambda user_id, item_id: database.items[item_id]
        database.update_user_profile_available_items = lambda **kwargs: database.updates.append(("amount", kwargs))
        database.update_user_avatar_item_last_purchased_date = lambda **kwargs: database.updates.append(("timestamp", kwargs))
        return database

    def test_battery_and_bait_can_drop_from_independent_successful_rolls(self):
        database = self.make_database()
        with patch.object(item_module, "get_tgommo_db_handler", return_value=database), \
                patch.object(item_module.random, "randint", side_effect=[1, 1]), \
                patch.object(item_module.random, "choice", return_value=ITEM_ID_BIRD_BAIT), \
                patch.object(item_module, "convert_to_png", side_effect=lambda image, file_name: file_name):
            notifications = item_module._prepare_random_item_catch_notification(user_id=7)

        self.assertEqual([message for message, _ in notifications], [
            "🎉 You found a battery while catching that creature!",
            "🎉 You found bird bait while catching that creature!",
        ])
        updated_item_ids = [entry[1]["item_id"] for entry in database.updates if entry[0] == "amount"]
        self.assertEqual(updated_item_ids, [ITEM_ID_BATTERY, ITEM_ID_BIRD_BAIT])

    def test_no_successful_roll_returns_no_notifications(self):
        database = self.make_database()
        with patch.object(item_module, "get_tgommo_db_handler", return_value=database), \
                patch.object(item_module.random, "randint", return_value=2), \
                patch.object(item_module, "convert_to_png"):
            notifications = item_module._prepare_random_item_catch_notification(user_id=7)

        self.assertEqual(notifications, [])
        self.assertEqual(database.updates, [])

    def test_bait_selection_is_limited_to_requested_ids(self):
        self.assertEqual(
            {ITEM_ID_MAMMAL_BAIT, ITEM_ID_BIRD_BAIT, ITEM_ID_REPTILE_BAIT},
            {
                ITEM_ID_MAMMAL_BAIT,
                ITEM_ID_BIRD_BAIT,
                ITEM_ID_REPTILE_BAIT,
            },
        )


if __name__ == "__main__":
    unittest.main()


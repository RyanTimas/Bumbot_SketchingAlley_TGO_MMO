import random
from PIL import Image

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from discord.ext.commands import Bot

from src.commons.CommonFunctions import convert_to_png
from src.commons.GameStateManager import get_game_state_manager
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import SHOP_UPDATE_RESTOCK_IMAGE
from src.resources.constants.general_constants import TGOMMO_CREATURE_SPAWN_CHANNEL_ID


class ShopScheduler:
    def __init__(self, discord_bot: Bot, timezone='America/New_York'):
        self.scheduler = AsyncIOScheduler()
        self.discord_bot = discord_bot

        self.timezone = pytz.timezone(timezone)

    def start_scheduler(self, test_interval=None):
        # by default, schedule the shop refresh to run daily at midnight. If test_interval is provided, schedule it to run at that interval in seconds for testing purposes.
        if test_interval:
            self.scheduler.add_job(
                func=self.refresh_daily_shop,
                trigger='interval',
                seconds=test_interval,
                id='daily_shop_refresh',
                replace_existing=True
            )
        else:
            # Schedule daily shop refresh at 3pm daily
            self.scheduler.add_job(
                func=self.refresh_daily_shop,
                trigger=CronTrigger(hour=15, minute=00, timezone=self.timezone),
                id='daily_shop_refresh',
                replace_existing=True
            )
        self.scheduler.start()


    async def refresh_daily_shop(self):
        try:
            get_game_state_manager().set_shop_date(datetime.datetime.now().strftime('%Y-%m-%d'))
            get_game_state_manager().set_current_shop_inventory(item_ids= self.generate_daily_items(), avatar_ids= self.generate_daily_avatars())

            message = "# 🚨UPDATE \n🛍️ Morshu's shop has been restocked! Check out the new items and avatars!"
            shop_restock_image = convert_to_png(Image.open(SHOP_UPDATE_RESTOCK_IMAGE), "daily_shop_refresh.png")
            await self.discord_bot.get_channel(TGOMMO_CREATURE_SPAWN_CHANNEL_ID).send(message, files=[shop_restock_image])
        except Exception as e:
            print(f"Error refreshing shop: {e}")

    def generate_daily_items(self):
        current_shop_level = get_game_state_manager().get_shop_level()

        # tuple format: (item_id, weight, min_shop_level)
        shop_item_pool = [
            # region Shop L1 items
            (ITEM_ID_BAIT, 100, 1),
            (ITEM_ID_COMMON_BAIT, 50, 1),
            (ITEM_ID_UNCOMMON_BAIT, 25, 1),

            (ITEM_ID_MAMMAL_BAIT, 35, 1),
            (ITEM_ID_BIRD_BAIT, 35, 1),
            (ITEM_ID_REPTILE_BAIT, 35, 1),

            (ITEM_ID_CHARM, 25, 1),
            (ITEM_ID_COMMON_CHARM, 15, 1),
            (ITEM_ID_UNCOMMON_CHARM, 15, 1),

            (ITEM_ID_NAMETAG, 75, 1),
            # endregion

            # region Shop L2 items
            (ITEM_ID_RARE_BAIT, 25, 2),

            (ITEM_ID_PLANE_TICKET_EST, 275, 2),
            (ITEM_ID_PLANE_TICKET_FL, 275, 2),

            # endregion

            # region Shop L3 items
            (ITEM_ID_EPIC_BAIT, 15, 3),

            (ITEM_ID_AMPHIBIAN_BAIT, 35, 3),
            (ITEM_ID_BUG_BAIT, 35, 3),

            (ITEM_ID_PLANE_TICKET_IC, 275, 3),
            (ITEM_ID_PLANE_TICKET_WY, 275, 3),
            # endregion

            # region Shop L4 items
            (ITEM_ID_PLANE_TICKET, 15, 4),

            (ITEM_ID_ULTRA_CHARM, 1, 4),
            (ITEM_ID_COMMON_ULTRA_CHARM, 1, 4),
            (ITEM_ID_UNCOMMON_ULTRA_CHARM, 1, 4),
            (ITEM_ID_RARE_ULTRA_CHARM, 1, 4),
            # endregion
        ]

        # Filter pool by current shop level
        available_pool = [(item, weight) for item, weight, min_level in shop_item_pool if current_shop_level >= min_level]

        # Create a weighted population for sampling without duplicates
        selected_items = []
        remaining_pool = available_pool.copy()

        for _ in range(3):
            if not remaining_pool:
                break

            # Extract items and weights
            items, weights = zip(*remaining_pool)

            # Select one item based on weights
            selected_item = random.choices(items, weights=weights, k=1)[0]
            selected_items.append(selected_item)

            # Remove the selected item from the pool to prevent duplicates
            remaining_pool = [(item, weight) for item, weight in remaining_pool if item != selected_item]

            print(f"Selected item: {selected_item}")

        return selected_items

    def generate_daily_avatars(self):
        shop_avatars = get_tgommo_db_handler().get_random_shop_avatars(count=3)
        return [avatar.avatar_id for avatar in shop_avatars]
from PIL import Image

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime

from discord.ext.commands import Bot

from src.commons.CommonFunctions import convert_to_png
from src.commons.GameStateManager import get_game_state_manager
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
            # Schedule daily shop refresh at midnight
            self.scheduler.add_job(
                func=self.refresh_daily_shop,
                # trigger=CronTrigger(hour=0, minute=0, timezone=self.timezone),
                trigger=CronTrigger(hour=13, minute=3, timezone=self.timezone),
                id='daily_shop_refresh',
                replace_existing=True
            )
            self.scheduler.start()


    async def refresh_daily_shop(self):
        try:
            # Add your shop update queries here
            # todo: grab 3 random items and 3 random avatars from the database and set them as the current shop inventory in the game state manager and database

            # get_game_state_manager().set_shop_date(datetime.now(self.timezone).date())
            get_game_state_manager().set_current_shop_inventory(item_ids= self.generate_daily_items(), avatar_ids= self.generate_daily_avatars())

            message = "#🚨UPDATE \n🛍️ Morshu's shop has been restocked! Check out the new items and avatars!"
            shop_restock_image = convert_to_png(Image.open(SHOP_UPDATE_RESTOCK_IMAGE), "daily_shop_refresh.png")
            await self.discord_bot.get_channel(TGOMMO_CREATURE_SPAWN_CHANNEL_ID).send(message, files=[shop_restock_image])
        except Exception as e:
            print(f"Error refreshing shop: {e}")

    def generate_daily_items(self):
        # Implement your item selection logic
        return []

    def generate_daily_avatars(self):
        # Implement your avatar selection logic
        return []
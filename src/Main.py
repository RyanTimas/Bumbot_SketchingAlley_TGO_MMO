import asyncio
import threading
import os
import certifi

from src.resources.constants.file_paths import OUTPUT_DIR, LOGS_DIR

# Point Python's SSL to certifi bundle before any network libs import
os.environ['SSL_CERT_FILE'] = certifi.where()
from src.commons.GameStateManager import initialize_game_state_manager
from src.database.handlers.DatabaseHandler import initialize_database, get_tgommo_db_handler
from src.caching.cache_registry import initialize_static_content_cache_registry
from src.caching.cache_startup import StartupCacheInitializer
from src.resources.constants.general_constants import *
from src.discord.DiscordBot import DiscordBot


def initialize_discord_bot():
    discord_bot = DiscordBot(token=DISCORD_TOKEN)
    discord_bot.start_bot()

"""Create necessary project directories on startup"""
def initialize_project_directories():
    # add to this if we need to make sure any more directories exist on startup
    directories = [
        OUTPUT_DIR,
        LOGS_DIR,
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def initialize_caching():
    # create a registry for keeping database info in memory for faster access and to avoid repeated database calls
    initialize_static_content_cache_registry(db_provider=get_tgommo_db_handler)
    StartupCacheInitializer().initialize()


async def main():
    threads = []

    # create necessary directories for the project, logs and output for now
    initialize_project_directories()

    # create a link between the sqlite database and the application so we can use it to store and retrieve data
    initialize_database()

    # create a registry for keeping database info in memory for faster access and to avoid repeated database calls
    initialize_caching()

    # create a game state manager to keep track of information that should be available even after the application is restarted, such as the current environment
    initialize_game_state_manager()

    if RUN_DISCORD_BOT:
        discord_thread = threading.Thread(target=initialize_discord_bot, args=(), daemon=True)
        threads.append(discord_thread)
        discord_thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    asyncio.run(main())
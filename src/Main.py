import asyncio
import threading
import os
import certifi

from src.resources.constants.file_paths import OUTPUT_DIR, LOGS_DIR

# Point Python's SSL to certifi bundle before any network libs import
os.environ['SSL_CERT_FILE'] = certifi.where()
import os
from src.commons.GameStateManager import initialize_game_state_manager
from src.database.handlers.DatabaseHandler import initialize_database
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


async def main():
    threads = []
    initialize_project_directories()
    initialize_database()
    initialize_game_state_manager()

    if RUN_DISCORD_BOT:
        discord_thread = threading.Thread(target=initialize_discord_bot, args=(), daemon=True)
        threads.append(discord_thread)
        discord_thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    asyncio.run(main())
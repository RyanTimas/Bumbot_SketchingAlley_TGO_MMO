import asyncio
import threading
import os
import certifi

# Point Python's SSL to certifi bundle before any network libs import
os.environ['SSL_CERT_FILE'] = certifi.where()

from src.commons.GameStateManager import initialize_game_state_manager
from src.database.handlers.DatabaseHandler import initialize_database
from src.resources.constants.general_constants import *
from src.discord.DiscordBot import DiscordBot


def initialize_discord_bot():
    discord_bot = DiscordBot(token=DISCORD_TOKEN)
    discord_bot.start_bot()


async def main():
    threads = []
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
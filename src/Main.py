import asyncio
import threading

from src.database.handlers.DatabaseHandler import initialize_database
from src.discord.general.commands import DiscordBotCommands
from src.resources.constants.general_constants import *
from src.discord.DiscordBot import DiscordBot


def initialize_discord_bot():
    # Initialize discord Bot
    discord_bot = DiscordBot(token=DISCORD_TOKEN)
    DiscordBotCommands.initialize_discord_commands(discord_bot)

    # Start the bot
    discord_bot.run()


async def main():
    threads = []
    initialize_database()

    if RUN_DISCORD_BOT:
        discord_thread = threading.Thread(target=initialize_discord_bot, args=(), daemon=True)
        threads.append(discord_thread)
        discord_thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    asyncio.run(main())
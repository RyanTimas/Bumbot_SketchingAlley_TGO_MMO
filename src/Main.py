import asyncio
import threading

from src.discord.commands import DiscordBotCommands
from src.resources.constants.general_constants import *
from src.discord.DiscordBot import DiscordBot
from obs.OBSWebsocket import OBSWebSocket
from twitch.TwitchBot import TwitchBot

def initialize_discord_bot():
    # Initialize discord Bot
    discord_bot = DiscordBot(token=DISCORD_TOKEN)
    DiscordBotCommands.assign_general_discord_commands(discord_bot)

    # Start the bot
    discord_bot.run()

async def main():
    threads = []
    if RUN_DISCORD_BOT:
        discord_thread = threading.Thread(target=initialize_discord_bot, args=(), daemon=True)
        threads.append(discord_thread)
        discord_thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    asyncio.run(main())
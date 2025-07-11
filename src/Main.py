import asyncio
import threading

from src.resources.general_constants import *
from src.discord.DiscordBot import DiscordBot
from obs.OBSWebsocket import OBSWebSocket
from twitch.TwitchBot import TwitchBot

def initialize_discord_bot(obs_websocket=None):
    # Initialize discord Bot
    discord_bot = DiscordBot(token=DISCORD_TOKEN)

    # Start the bot
    discord_bot.run()

async def initialize_twitch_bot(obs_websocket=None):
    # Initialize Twitch Bot
    twitch_bot = TwitchBot(client_id=TWITCH_CLIENT_ID, app_secret=TWITCH_APP_SECRET, target_channel=TWITCH_TARGET_CHANNEL, refresh_token= ACCESS_TOKEN, access_token= REFRESH_TOKEN, obs_websocket=obs_websocket)
    await twitch_bot.run_bot()

async def main():
    obs_websocket = None
    discord_bot = None

    if RUN_OBS_BOT:
        # Initialize OBS WebSocket
        obs_websocket = OBSWebSocket(host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD)

        if not obs_websocket.connect():
            print("Failed to connect to OBS, exiting...")
            return

    threads = []
    if RUN_DISCORD_BOT:
        discord_thread = threading.Thread(target=initialize_discord_bot, args=(obs_websocket,), daemon=True)
        threads.append(discord_thread)
        discord_thread.start()

    if RUN_TWITCH_BOT:
        await initialize_twitch_bot(obs_websocket)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    asyncio.run(main())
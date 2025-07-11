import discord
from discord.ext import commands
from discord.ext.commands import Bot

class DiscordBot:
    discord_bot: Bot= commands.Bot(command_prefix='!', intents=discord.Intents.all())

    def __init__(self, token: str):
        self.token = token

        # Register event handlers
        self.discord_bot.event(self.on_ready)


    @discord_bot.event
    async def on_ready(self):
        print(f'DiscordBot - Logged in as {self.discord_bot.user.name} ({self.discord_bot.user.id})')


    def run(self):
        self.discord_bot.run(self.token)
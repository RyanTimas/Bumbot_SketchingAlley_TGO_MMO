import discord
from discord.ext import commands
from discord.ext.commands import Bot

from src.database.handlers.DatabaseHandler import DatabaseHandler
from src.discord.handlers.CreatureSpawnerHandler import CreatureSpawnerHandler


class DiscordBot:
    discord_bot: Bot= commands.Bot(command_prefix='!', intents=discord.Intents.all())

    def __init__(self, token: str):
        self.token = token

        # Register event handlers
        self.discord_bot.event(self.on_ready)
        self.creature_spawner_handler = CreatureSpawnerHandler(self.discord_bot)

    @discord_bot.event
    async def on_ready(self):
        print(f'DiscordBot - Logged in as {self.discord_bot.user.name} ({self.discord_bot.user.id})')
        self.creature_spawner_handler.start_creature_spawner()


    def run(self):
        self.discord_bot.run(self.token)
import asyncio
import threading
import time
from copy import deepcopy
import random
import discord

from discord.ext.commands import Bot
from src.database.handlers import DatabaseHandler
from src.discord.buttonhandlers.CatchButton import TGOMMOCatchButtonView
from src.discord.embeds.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.objects.CreatureRarity import MYTHICAL, get_rarity
from src.discord.objects.TGOCreature import TGOCreature, TEST_SPAWN_POOL
from src.resources.constants.general_constants import DISCORD_SA_CHANNEL_ID_TEST


class CreatureSpawnerHandler:
    def __init__(self, discord_bot: Bot, database_handler: DatabaseHandler):
        self.discord_bot = discord_bot
        self.database_handler = database_handler

        self.are_creatures_spawning = True


    def start_creature_spawner(self):
        asyncio.create_task(self._creature_spawner())


    def toggle_creature_spawner(self, ctx):
        self.are_creatures_spawning = not self.are_creatures_spawning
        return "creatures are now spawning" if self.are_creatures_spawning else "creatures are no longer spawning"


    async def _creature_spawner(self):
        while self.spawn_creature:
            await self.spawn_creature(creature= await self.creature_picker())

            # wait between 1 and 10 minutes before spawning another creature
            await asyncio.sleep(random.uniform(1, 10) * 60 )  # 5 minutes


    async def spawn_creature(self, creature: TGOCreature):
        creature_embed = CreatureEmbedHandler(creature=creature).generate_spawn_embed()

        # Send a message to the approval queue with a button to give XP
        spawn_message = await self.discord_bot.get_channel(DISCORD_SA_CHANNEL_ID_TEST).send(
            view=TGOMMOCatchButtonView(discord_bot=self.discord_bot, message=f'Catch',database_handler=self.database_handler,creature=creature),
            files=[creature_embed[1], creature_embed[2]],
            embed=creature_embed[0]
        )

        # Create separate task for despawn
        thread = threading.Thread(target=self._handle_despawn, args=(creature, spawn_message))
        thread.daemon = True
        thread.start()

    def _handle_despawn(self, creature: TGOCreature, spawn_message):
        time.sleep(creature.despawn_time)
        try:
            # Try to fetch the message to check if it still exists
            channel = self.discord_bot.get_channel(spawn_message.channel.id)
            asyncio.run_coroutine_threadsafe(channel.fetch_message(spawn_message.id), self.discord_bot.loop).result()
        except discord.NotFound:
            print('Message was already deleted, do nothing')
            return

        creature_embed = CreatureEmbedHandler(creature=creature).generate_spawn_embed(is_spawn_message=False)
        asyncio.run_coroutine_threadsafe(spawn_message.delete(), self.discord_bot.loop)
        asyncio.run_coroutine_threadsafe(
            self.discord_bot.get_channel(DISCORD_SA_CHANNEL_ID_TEST).send(
                files=[creature_embed[1]],
                embed=creature_embed[0]
            ), self.discord_bot.loop
        )

    async def creature_picker(self):
        rarity = get_rarity()
        available_creatures = [creature for creature in TEST_SPAWN_POOL if creature.rarity == rarity]

        selected_creature = deepcopy(available_creatures[random.randint(0, len(available_creatures)-1) if len(available_creatures) > 1 else 0])

        if random.randint(0,10) == 1:
            selected_creature.rarity = MYTHICAL
            selected_creature.img_path += '_S'

        return selected_creature


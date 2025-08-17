import asyncio
from datetime import datetime
import random
import discord

from discord.ext.commands import Bot
from src.database.handlers import DatabaseHandler
from src.discord.buttonhandlers.CatchButton import CatchButton, TGOMMOCatchButtonView
from src.discord.handlers.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import N01_CHIPMUNK_IMAGE_FILE
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
        ctx.channel.send("creatures are now spawning" if self.are_creatures_spawning else "creatures are no longer spawning", delete_after=5)


    async def _creature_spawner(self):
        while self.spawn_creature:
            await self.spawn_creature(creature= await self.creature_picker())
            await asyncio.sleep(random.uniform(60, 600) )  # 5 minutes


    async def spawn_creature(self, creature: TGOCreature):
        creature_embed = await CreatureEmbedHandler(creature=creature).generate_spawn_embed()

        # Send a message to the approval queue with a button to give XP
        spawn_message = await self.discord_bot.get_channel(DISCORD_SA_CHANNEL_ID_TEST).send(
            #content=f"## A Wild {creature.name} has appered!!\n Be the first to hit the catch button to claim!!",
            view=TGOMMOCatchButtonView(discord_bot=self.discord_bot, message=f'Catch',database_handler=self.database_handler),
            files=[creature_embed[1], creature_embed[2]],
            embed=creature_embed[0]
        )

        await asyncio.sleep(creature.despawn_time * 60)
        try:
            creature_embed = await CreatureEmbedHandler(creature=creature).generate_spawn_embed(is_spawn_message=False)

            await spawn_message.delete()
            await self.discord_bot.get_channel(DISCORD_SA_CHANNEL_ID_TEST).send(
                files=[creature_embed[1], creature_embed[2]],
                embed=creature_embed[0]
            )
        except discord.NotFound:
            # Message was deleted, so nothing to edit
            pass


    async def creature_picker(self):
        return TGOCreature(name='Test Creature', img_path=N01_CHIPMUNK_IMAGE_FILE,  rarity='common')
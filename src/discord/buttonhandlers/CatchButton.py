import asyncio
from datetime import datetime

import discord
from discord import Message
from discord.ui import View

from src.database.handlers import DatabaseHandler
from src.database.handlers.DatabaseHandler import get_db_handler, get_tgommo_db_handler, get_user_db_handler
from src.discord.embeds.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.objects.CreatureRarity import MYTHICAL
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment


class CatchButton(discord.ui.Button):
    # Class-level lock for synchronization
    _lock = asyncio.Lock()

    def __init__(self, discord_bot, message: Message, creature:TGOCreature, environment:TGOEnvironment):
        super().__init__(label="Catch Critter!!", style=discord.ButtonStyle.blurple)
        self.discord_bot = discord_bot
        self.message = message
        self.creature = creature
        self.environment = environment
        self.caught = False  # Track if creature has been caught



    async def callback(self, interaction: discord.Interaction):
        # Use lock to ensure only one user can catch at a time
        async with self._lock:
            # Check if creature was already caught
            if self.caught:
                await interaction.response.send_message("Someone else already caught this creature!", ephemeral=True)
                return
            # Mark as caught immediately to prevent others from catching
            self.caught = True

        # generate the successful catch embed
        successful_catch_embed = CreatureEmbedHandler(self.creature, self.environment).generate_catch_embed(interaction=interaction)
        total_xp = successful_catch_embed[3]

        # insert record of user catching the creature
        get_tgommo_db_handler().insert_new_user_creature(params=(interaction.user.id, self.creature.creature_id, self.creature.variant_no, self.environment.environment_id, self.creature.rarity == MYTHICAL))
        # give user xp for catching the creature
        get_user_db_handler().update_xp(total_xp, interaction.user.id, interaction.user.display_name)

        # send a message to the channel announcing the successful catch
        await interaction.channel.send(embed=successful_catch_embed[0], files=[successful_catch_embed[1]])

        # send a personal message to user confirming the catch
        await interaction.response.send_message(f"Success!! you've successfully caught {self.creature.name}", ephemeral=True)

        # delete the original spawn message so nobody else can catch it
        try:
            await interaction.message.delete()
        except discord.errors.NotFound:
            print('Message was already deleted, do nothing')


class TGOMMOCatchButtonView(View):
    def __init__(self, discord_bot, message, creature:TGOCreature, environment:TGOEnvironment):
        super().__init__(timeout=None)
        self.add_item(CatchButton(discord_bot=discord_bot, message=message, creature=creature, environment=environment))
import asyncio

import discord
from discord import Message
from discord.ui import View

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler, get_user_db_handler
from src.discord.buttonhandlers.creature_enounter.CreatureCaughtView import CreatureCaughtView
from src.discord.embeds.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.handlers.AvatarUnlockHandler import AvatarUnlockHandler
from src.discord.objects.CreatureRarity import *
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import USER_CATCHES_DAILY, USER_CATCHES_HOURLY


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

        self.successful_catch_embed_handler = None
        self.successful_catch_message = None


    async def callback(self, interaction: discord.Interaction):
        # Use lock to ensure only one user can catch at a time
        async with self._lock:
            # Check if creature was already caught
            if self.caught:
                await interaction.response.send_message("Someone else already caught this creature...", ephemeral=True)
                return

            # Mark as caught immediately to prevent others from catching
            can_catch, catch_message = await self._handle_user_catch_limits(interaction.user.id, self.creature.creature_id)
            self.caught = can_catch

            # can always catch mythical creatures
            if not can_catch and self.creature.rarity != MYTHICAL:
                await interaction.response.send_message(catch_message, ephemeral=True)
                return

        # generate the successful catch embed
        self.successful_catch_embed_handler = CreatureEmbedHandler(self.creature, self.environment)
        successful_catch_embed = self.successful_catch_embed_handler.generate_catch_embed(interaction=interaction)
        total_xp = successful_catch_embed[2]

        # insert record of user catching the creature & give user xp for catching the creature
        catch_id = get_tgommo_db_handler().insert_new_user_creature(params=(interaction.user.id, self.creature.creature_id, self.creature.variant_no, self.environment.environment_id, self.creature.rarity == MYTHICAL))
        get_user_db_handler().update_xp(total_xp, interaction.user.id, interaction.user.display_name)

        # send a message to the channel announcing the successful catch
        self.successful_catch_message = await interaction.channel.send(embed=successful_catch_embed[0], files=[successful_catch_embed[1]])

        # send a personal message to user confirming the catch
        await self.handle_successful_catch_response(interaction, catch_id)

        await AvatarUnlockHandler(user_id=interaction.user.id, interaction=interaction).check_avatar_unlock_conditions()

        # delete the original spawn message so nobody else can catch it
        try:
            await interaction.message.delete()
        except discord.errors.NotFound:
            print('Message was already deleted, do nothing')


    async def handle_successful_catch_response(self, interaction: discord.Interaction, catch_id: int):
        nickname_view = CreatureCaughtView(interaction=interaction, creature_id=catch_id, successful_catch_embed_handler=self.successful_catch_embed_handler, successful_catch_message=self.successful_catch_message)
        await interaction.response.send_message(f"Success!! you've successfully caught the {self.creature.name}", view=nickname_view, ephemeral=True)


    async def _handle_user_catch_limits(self, user_id, creature_id):
        if self.creature.rarity.name == MYTHICAL.name:
            return True  # Mythical creatures can always be caught

        # handle hourly catch limits
        if user_id in USER_CATCHES_HOURLY:
            if USER_CATCHES_HOURLY[user_id] >= 12:
                return False, "You're catching guys too fast save some for the rest of us! Try again at the top of the hour.",
            else:
                USER_CATCHES_HOURLY[user_id] += 1
        else:
            USER_CATCHES_HOURLY[user_id] = 1

        # handle daily catch limits
        if user_id in USER_CATCHES_DAILY:
            count_for_creature = sum(1 for cid in USER_CATCHES_DAILY[user_id] if cid == creature_id)
            too_many_catches = False
            if self.creature.rarity.name == LEGENDARY.name:
                too_many_catches = count_for_creature >= 1
            elif self.creature.rarity.name == EPIC.name:
                too_many_catches = count_for_creature >= 1
            elif self.creature.rarity.name == RARE.name:
                too_many_catches = count_for_creature >= 3
            elif self.creature.rarity.name == UNCOMMON.name:
                too_many_catches = count_for_creature >= 5
            elif self.creature.rarity.name == COMMON.name:
                too_many_catches = count_for_creature >= 10

            if too_many_catches:
                return False, f"You've reached the {self.creature.name} catch limit today! You can more again tomorrow.",
            else:
                USER_CATCHES_DAILY[user_id] += (creature_id,)
                return True, ""
        else:
            USER_CATCHES_DAILY[user_id] = (creature_id,)
            return True, ""


class TGOMMOEncounterView(View):
    def __init__(self, discord_bot, message, creature:TGOCreature, environment:TGOEnvironment):
        super().__init__(timeout=None)
        self.add_item(CatchButton(discord_bot=discord_bot, message=message, creature=creature, environment=environment))
import asyncio
import time

from discord.ui import View

from src.commons.CommonDecorators import measure_execution_time, retry_on_ssl_error
from src.commons.CommonFunctions import convert_to_png, check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler, get_user_db_handler
from src.discord.game_features.creature_enounter.CatchFunctions import catch_creature
from src.discord.game_features.creature_enounter.CreatureCaughtView import CreatureCaughtView
from src.discord.game_features.creature_enounter.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.handlers.AvatarUnlockHandler.AvatarUnlockHandler import check_for_event_avatars, \
    check_for_quest_avatars, check_for_special_quest_avatars
from src.discord.handlers.ItemUnlockHandler.ItemUnlockHandler import check_for_milestone_catch_rewards
from src.discord.objects.CreatureRarity import *
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.discord.objects.TGOPlayer import TGOPlayer
from src.resources.constants.TGO_MMO_constants import USER_CATCHES_DAILY, USER_CATCHES_HOURLY


class CreatureEncounterView(View):
    def __init__(self, discord_bot, creature:TGOCreature, environment:TGOEnvironment, spawn_user:TGOPlayer = None):
        super().__init__(timeout=None)
        self.discord_bot = discord_bot

        self.creature = creature
        self.environment = environment
        self.spawn_user = spawn_user

        self.caught = False

        self.interaction_lock = asyncio.Lock()
        self.successful_catch_embed_handler = None
        self.successful_catch_message = None

        self.add_item(self.create_catch_button())
        self.add_item(self.is_creature_caught_button())

    def create_catch_button(self, row=0):
        button = discord.ui.Button(label="Catch Critter!!", style=discord.ButtonStyle.blurple, row=row)
        button.callback = self.catch_button_callback()
        return button
    def catch_button_callback(self,):
        @retry_on_ssl_error(max_retries=3, delay=1)
        @measure_execution_time(label="Catch Button Callback Execution Time")
        async def callback(interaction):
            self.creature.catch_time = time.time()
            await interaction.response.defer()

            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, None if not self.spawn_user else self.spawn_user.user_id):
                return

            # Double check creature hasn't already been caught while waiting for interaction lock
            async with self.interaction_lock:
                if self.caught:
                    await interaction.response.send_message("Someone else already caught this creature...", ephemeral=True)
                    return

                self.caught, catch_message = self._handle_user_catch_limits(interaction.user.id, self.creature.creature_id)
                if not self.caught:
                    await interaction.response.send_message(catch_message, ephemeral=True)
                    return

            # generate the successful catch embed
            await interaction.followup.send(f"Please wait...", ephemeral=True)

            result = catch_creature(interaction.user.id, self.creature, self.environment, spawn_user=self.spawn_user)
            catch_id = result["catch_id"]

            # send a message to the channel announcing the successful catch
            self.successful_catch_embed_handler = CreatureEmbedHandler(self.creature, self.environment, spawn_user= self.spawn_user)
            self.successful_catch_message = await interaction.channel.send(embed=result["catch_embed"], files=[result["catch_image"]])

            # send a personal message to user confirming the catch & seeing if they have unlocked a new avatar
            nickname_view = CreatureCaughtView(user_id=interaction.user.id, creature_catch_id=catch_id, successful_catch_embed_handler=self.successful_catch_embed_handler, successful_catch_message=self.successful_catch_message)

            # check if player has unlocked any avatars based on their catch and unlock them if they haven't already been unlocked
            await check_for_event_avatars(user_id=interaction.user.id, interaction=interaction)
            await check_for_quest_avatars(user_id=interaction.user.id, interaction=interaction)
            await check_for_special_quest_avatars(user_id=interaction.user.id, creature=self.creature, interaction=interaction)

            # check if player has unlocked any items based on their catch and unlock them if they haven't already been unlocked
            await  check_for_milestone_catch_rewards(user_id=interaction.user.id, interaction=interaction)

            # delete the original spawn message so nobody else can catch it
            try:
                await interaction.message.delete()
            except discord.errors.NotFound:
                print('Message was already deleted, do nothing')

            # once all processing is done, send the success message to the user
            await interaction.followup.send(f"Success!! you've successfully caught the {self.creature.name}", view=nickname_view, ephemeral=True)
        return callback

    def is_creature_caught_button(self, row=0):
        button = discord.ui.Button(label="Analyze Creature", style=discord.ButtonStyle.gray, emoji="🔎", row=row)
        button.callback = self.creature_analyze_button_callback()
        return button
    def creature_analyze_button_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Get user's creatures and count this species
            total_catches_for_species = get_tgommo_db_handler().get_total_catches_for_creature_by_user(user_id=interaction.user.id, dex_no=self.creature.dex_no)
            total_catches_for_variant = get_tgommo_db_handler().get_total_catches_for_creature_variant_by_user(user_id=interaction.user.id, creature_id=self.creature.creature_id)
            total_catches_for_variant_in_environment = get_tgommo_db_handler().get_total_catches_for_species_for_environment(user_id=interaction.user.id, creature_id=self.creature.creature_id, environment_dex_no=self.environment.dex_no)
            total_mythical_catches_for_variant = get_tgommo_db_handler().get_total_mythical_catches_for_creature_variant_by_user(user_id=interaction.user.id, creature_id=self.creature.creature_id)

            # Check for complete message overrides first
            if total_catches_for_species == 0:
                message = f"# ‼️You've never caught this creature before!‼️"
            elif total_mythical_catches_for_variant == 0 and self.creature.local_rarity == MYTHICAL:
                message = f"# ⭐You've never caught the Mythical form of this creature before!⭐"
            else:
                # Build the detailed message with conditional formatting
                creature_name = f"{self.creature.full_name}" + (f" ({self.creature.variant_name})" if self.creature.variant_name else "")
                variant_line = "‼️You never caught this form for this creature before!🔥" if total_catches_for_variant == 0 else f"🔥Catches For Variant: **{total_catches_for_variant}**"
                environment_line = "‼️You've never caught this creature in this environment before!🌎" if total_catches_for_variant_in_environment == 0 else f"🌎 Catches For Variant in Environment: **{total_catches_for_variant_in_environment}**"

                message = (
                    f"# 🔍 {creature_name} - Total Catches: **{total_catches_for_species}**\n"
                    f"### * {variant_line}\n"
                    f"### * {environment_line}\n"
                    f"### * ⭐ Mythical catches For Variant: **{total_mythical_catches_for_variant}**"
                )

            await interaction.response.send_message(message, files=[convert_to_png(self.creature.creature_image, file_name="creature_img.png")], ephemeral=True)
        return callback

    # Support Functions
    def _handle_user_catch_limits(self, user_id, creature_id):
        # Storage being full always takes precedence
        if get_tgommo_db_handler().get_total_catches_for_user(user_id=user_id, is_released=False) >= get_tgommo_db_handler().get_creature_inventory_expansions_by_user_id(user_id=user_id) * 100:
            return False, "Your creature inventory is full! Please release some creatures before catching more.",

        # Mythical creatures & spawned creatures can always be caught
        if self.creature.local_rarity.name == MYTHICAL.name or self.spawn_user:
            return True, ""

        # handle hourly catch limits
        if user_id in USER_CATCHES_HOURLY:
            if USER_CATCHES_HOURLY[user_id] >= 12:
                # TODO: THIS IS A BANDAID SOLUTION, USER CATCHES NOT RESETTING PROPERLY. FIX THIS LATER
                return True, "",
                # return False, "You're catching guys too fast save some for the rest of us! Try again at the top of the hour.",
            else:
                USER_CATCHES_HOURLY[user_id] += 1
        else:
            USER_CATCHES_HOURLY[user_id] = 1

        # handle daily catch limits
        if user_id in USER_CATCHES_DAILY:
            count_for_creature = sum(1 for cid in USER_CATCHES_DAILY[user_id] if cid == creature_id)
            too_many_catches = False
            if self.creature.local_rarity.name == LEGENDARY.name:
                too_many_catches = count_for_creature >= 1
            elif self.creature.local_rarity.name == EPIC.name:
                too_many_catches = count_for_creature >= 1
            elif self.creature.local_rarity.name == RARE.name:
                too_many_catches = count_for_creature >= 3
            elif self.creature.local_rarity.name == UNCOMMON.name:
                too_many_catches = count_for_creature >= 5
            elif self.creature.local_rarity.name == COMMON.name:
                too_many_catches = count_for_creature >= 10

            if too_many_catches:
                # TODO: THIS IS A BANDAID SOLUTION, USER CATCHES NOT RESETTING PROPERLY. FIX THIS LATER
                return True, "",
                # return False, f"You've reached the {self.creature.name} catch limit today! You can more again tomorrow.",
            else:
                USER_CATCHES_DAILY[user_id] += (creature_id,)
                return True, ""
        else:
            USER_CATCHES_DAILY[user_id] = (creature_id,)
            return True, ""
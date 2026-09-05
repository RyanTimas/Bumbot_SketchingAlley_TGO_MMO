import asyncio
import time

from discord import errors, ButtonStyle
from discord.ui import View, Button

from src.commons.CommonDecorators import measure_execution_time, retry_on_ssl_error
from src.commons.CommonFunctions import convert_to_png, check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
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
from src.resources.constants.TGO_MMO_constants import USER_CATCHES_DAILY, USER_CATCHES_HOURLY, BASE_CREATURE_STORAGE_EXPANSIONS, MAX_CREATURE_STORAGE_EXPANSIONS, CREATURE_STORAGE_EXPANSION_BASE_COST, ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION


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
        button = Button(label="Catch Critter!!", style=ButtonStyle.blurple, row=row)
        button.callback = self.catch_button_callback()
        return button
    def catch_button_callback(self,):
        @retry_on_ssl_error(max_retries=3, delay=1)
        @measure_execution_time(label="Catch Button Callback Execution Time")
        async def callback(interaction):
            self.creature.catch_time = time.time()
            await interaction.response.defer(ephemeral=True)

            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, None if not self.spawn_user else self.spawn_user.user_id):
                return

            # Double check creature hasn't already been caught while waiting for interaction lock
            async with self.interaction_lock:
                if self.caught:
                    await interaction.followup.send("Someone else already caught this creature...", ephemeral=True)
                    return

                self.caught, catch_message, expansion_view = self._handle_user_catch_limits(interaction.user.id, self.creature.creature_id)
                if not self.caught:
                    if expansion_view:
                        await interaction.followup.send(catch_message, view=expansion_view, ephemeral=True)
                    else:
                        await interaction.followup.send(catch_message, ephemeral=True)
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
            except errors.NotFound:
                print('Message was already deleted, do nothing')

            # once all processing is done, send the success message to the user
            await interaction.followup.send(f"Success!! you've successfully caught the {self.creature.name}", view=nickname_view, ephemeral=True)
        return callback

    def is_creature_caught_button(self, row=0):
        button = Button(label="Analyze Creature", style=ButtonStyle.gray, emoji="🔎", row=row)
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

    '''---------------SUPPORTING FUNCTIONS---------------------------------------------------------------------------------------------------------'''
    def _handle_user_catch_limits(self, user_id, creature_id):
        # Storage being full always takes precedence
        if get_tgommo_db_handler().get_total_catches_for_user(user_id=user_id, is_released=False) >= get_tgommo_db_handler().get_creature_inventory_expansions_by_user_id(user_id=user_id) * 100:
            message, expansion_view = self.create_storage_expansion_view(user_id)
            return False, message, expansion_view
        return True, None, None

    def create_storage_expansion_view(self, user_id):
        """Builds and returns (message, view) for expanding creature storage for the given user_id.
        This mirrors the Create Storage Expansion button behavior in CreatureInventoryView.
        """
        message = "Your creature inventory is full! Please release some creatures before catching more."

        expansion_view = View(timeout=None)
        expansion_button = Button(label="Expand Storage ➕", style=ButtonStyle.green)

        async def expansion_button_callback(interaction):
            # Only allow the user who saw the message to expand their own storage
            if interaction.user.id != user_id:
                await interaction.response.send_message("You cannot expand someone else's storage.", ephemeral=True)
                return

            # Determine current pages and cost
            total_pages = get_tgommo_db_handler().get_creature_inventory_expansions_by_user_id(user_id=user_id)
            if total_pages + 1 > MAX_CREATURE_STORAGE_EXPANSIONS:
                await interaction.response.send_message("Your Storage is maxed out. It cannot be expanded any further.", ephemeral=True)
                return

            already_purchased_expansions = total_pages - BASE_CREATURE_STORAGE_EXPANSIONS
            expansion_cost = (already_purchased_expansions + 1) * CREATURE_STORAGE_EXPANSION_BASE_COST

            # Process payment and expansion using consistent DB API
            user_profile = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=user_id)
            if user_profile.currency < expansion_cost:
                await interaction.response.send_message("❌ You do not have enough coins to expand your creature storage.", ephemeral=True)
                return

            # Update DB: increment expansion item and deduct currency
            get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION, new_amount=total_pages + 1)
            get_tgommo_db_handler().update_user_profile_currency(user_id=user_id, new_currency=expansion_cost * -1)

            await interaction.response.send_message("✅ Your creature storage has been expanded by 100 slots!", ephemeral=True)
            return

        expansion_button.callback = expansion_button_callback
        expansion_view.add_item(expansion_button)

        return message, expansion_view

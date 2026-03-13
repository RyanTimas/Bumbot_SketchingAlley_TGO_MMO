import asyncio
from discord.ui import View

from src.commons.CommonFunctions import convert_to_png, interaction_guard, retry_on_ssl_error, \
    check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler, get_user_db_handler
from src.discord.game_features.creature_enounter.CreatureCaughtView import CreatureCaughtView
from src.discord.game_features.creature_enounter.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.general.handlers.AvatarUnlockHandler import AvatarUnlockHandler
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
        async def callback(interaction):
            await interaction.response.defer()
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, None if not self.spawn_user else self.spawn_user.user_id):
                return

            async with self.interaction_lock:
                # handle additional interaction logic here
                if self.caught:
                    await interaction.response.send_message("Someone else already caught this creature...", ephemeral=True)
                    return

                can_catch, catch_message = await self._handle_user_catch_limits(interaction.user.id, self.creature.creature_id)
                self.caught = can_catch

                if not can_catch:
                    await interaction.response.send_message(catch_message, ephemeral=True)
                    return

            # generate the successful catch embed
            self.successful_catch_embed_handler = CreatureEmbedHandler(self.creature, self.environment, spawn_user= self.spawn_user)
            successful_catch_embed, successful_catch_image, total_xp = self.successful_catch_embed_handler.generate_catch_embed(interaction=interaction)

            # insert record of user catching the creature & give user xp for catching the creature
            catch_id = get_tgommo_db_handler().insert_new_user_creature(params=(interaction.user.id, self.creature.creature_id, self.creature.variant_no, self.creature.environment_id, self.creature.local_rarity == MYTHICAL))
            get_user_db_handler().update_xp(total_xp, interaction.user.id, interaction.user.display_name)

            # send a message to the channel announcing the successful catch
            self.successful_catch_message = await interaction.channel.send(embed=successful_catch_embed, files=[successful_catch_image])

            # send a personal message to user confirming the catch & seeing if they have unlocked a new avatar
            await self.handle_successful_catch_response(interaction, catch_id)
            await AvatarUnlockHandler(user_id=interaction.user.id, interaction=interaction).check_avatar_unlock_conditions()

            # delete the original spawn message so nobody else can catch it
            try:
                await interaction.message.delete()
            except discord.errors.NotFound:
                print('Message was already deleted, do nothing')
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

            message = (
                f"You have caught **{total_catches_for_species}** {self.creature.name}(s) \n"
                f"You have caught **{total_catches_for_variant}** of this variant! \n"
                f"You have caught **{total_catches_for_variant_in_environment}** of this  in this environment! \n"
                f"You have caught **{total_mythical_catches_for_variant}** Mythical {self.creature.name}(s)!"
            )

            if total_catches_for_species == 0:
                message = f"# ‼️You've never caught this creature before!‼️"
            elif total_catches_for_variant == 0:
                message = f"🔥You never caught this form for this creature before!🔥"
            elif total_catches_for_variant_in_environment == 0:
                message = f"🌎You've never caught this creature in this environment before!🌎"
            elif total_mythical_catches_for_variant == 0 and self.creature.local_rarity == MYTHICAL:
                message = f"# ⭐You've never caught the Mythical form of this creature before!⭐"
            await interaction.response.send_message(message, files=[convert_to_png(self.creature.creature_image, file_name="creature_img.png")], ephemeral=True)
        return callback

    # Support Functions
    async def handle_successful_catch_response(self, interaction: discord.Interaction, catch_id: int):
        nickname_view = CreatureCaughtView(interaction=interaction, creature_catch_id=catch_id, successful_catch_embed_handler=self.successful_catch_embed_handler, successful_catch_message=self.successful_catch_message)
        await interaction.followup.send(f"Success!! you've successfully caught the {self.creature.name}",  view=nickname_view, ephemeral=True)

    async def _handle_user_catch_limits(self, user_id, creature_id):
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
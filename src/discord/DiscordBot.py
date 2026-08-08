import asyncio
import sys

import aiohttp
import discord
from PIL import Image
from discord.ext import commands

from src.commons.CommonDecorators import admin_only
from src.commons.CommonFunctions import get_user_discord_profile_pic, flip_coin, convert_to_png
from src.commons.GameStateManager import get_game_state_manager
from src.commons.GuildHandler import set_guild
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarBoardImageFactory import AvatarBoardImageFactory
from src.discord.game_features.avatar_board.AvatarBoardView import AvatarBoardView
from src.discord.game_features.creature_enounter.CreatureSpawnerHandler import CreatureSpawnerHandler
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.creature_inventory.CreatureInventoryView import CreatureInventoryView
from src.discord.game_features.encyclopedia.encyclopedia_location_index.EncyclopediaLocationIndexImageFactory import EncyclopediaLocationIndexImageFactory
from src.discord.game_features.encyclopedia.encyclopedia_location_index.EncyclopediaLocationIndexView import EncyclopediaLocationIndexView
from src.discord.game_features.item_inventory.ItemInventoryImageFactory import ItemInventoryImageFactory
from src.discord.game_features.item_inventory.ItemInventoryView import ItemInventoryView
from src.discord.game_features.player_profile.PlayerProfileImageFactory import PlayerProfileImageFactory
from src.discord.game_features.player_profile.PlayerProfileView import PlayerProfileView
from src.discord.game_features.shop.ShopImageFactory import ShopImageFactory
from src.discord.game_features.shop.ShopView import ShopView
from src.discord.game_features.trap_manager.TrapManagerImageFactory import TrapManagerImageFactory
from src.discord.game_features.trap_manager.TrapManagerView import TrapManagerView
from src.discord.tests.CreatureEncounterTests import register_creature_encounter_tests
from src.discord.tests.GeneralTests import register_general_tests
from src.discord.tests.ShopTests import register_shop_tests
from src.discord.tests.EncyclopediaTests import register_encyclopedia_tests
from src.discord.handlers.ScheduledServices.ShopScheduler import ShopScheduler
from src.discord.objects.CreatureRarity import MYTHICAL
from src.resources.constants.file_paths import IMAGE_FILE_EXTENSION, \
    TGOMMO_TRAVEL_ADVISORY_LANDING_BASE
from src.resources.constants.general_constants import TGOMMO_ACTIVE_SERVER_ID, DISCORD_USER_BLACKLIST, \
    TGOMMO_CREATURE_SPAWN_CHANNEL_ID


class DiscordBot(commands.Bot):
    def __init__(self, token: str,):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
        self.token = token

        # Register bot functionality
        self.register_events()

        self.register_core_commands()
        self.register_misc_feature_commands()

        self.register_tgommo_user_general_commands()
        self.register_tgommo_user_navigation_commands()
        self.register_tgommo_admin_commands()

        self.register_test_commands()

        self.creature_spawner_handler = CreatureSpawnerHandler(discord_bot=self)
        self.shop_restock_scheduler = ShopScheduler(discord_bot=self)


    '''---- EVENTS ----------------------------------------------------------------------------------------------------'''
    def register_events(self):
        @self.event
        async def on_ready():
            print(f'DiscordBot - Logged in as {self.user.name} ({self.user.id})')

            try:
                set_guild(self)
                print(f"Synced {len(await self.tree.sync(guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID)))} command(s) to guild")
            except Exception as e:
                print(f"Failed to sync commands: {e}")

            # Start scheduled tasks
            self.creature_spawner_handler.start_creature_spawner()
            self.shop_restock_scheduler.start_scheduler()

        @self.event
        async def on_message(message):
            if message.author.id in DISCORD_USER_BLACKLIST:
                return

            # SHINY CHECK
            if flip_coin(total_iterations=13):
                shiny_msg = await message.reply(f"```fix\n✨THIS MESSAGE IS A CERTIFIED SHINY!!✨\n```")
                await shiny_msg.reply(f"Took {get_game_state_manager().get_shiny_message_count()} messages to get a shiny")
                get_game_state_manager().set_shiny_message_count(new_count=0)
            else:
                shiny_message_count = get_game_state_manager().get_shiny_message_count()
                get_game_state_manager().set_shiny_message_count(new_count=shiny_message_count + 1)

            await self.process_commands(message)


        @self.event
        async def on_command_error(ctx, error):
            if isinstance(error, discord.ext.commands.CommandNotFound):
                # Silently ignore command not found errors
                return
            # Re-raise other errors so they aren't suppressed
            raise error

    '''---- SLASH COMMANDS ----------------------------------------------------------------------------------------------------'''
    def register_core_commands(self):
        @self.tree.command(name="shutdown", description="Completely shuts down bumbot. Please for emergencies only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def shutdown(interaction: discord.Interaction):
            print("Shutting down bot...")
            await interaction.response.send_message("Successfully shut down bot.", delete_after=5)

            # Close the Discord connection
            if self:
                await self.close()

            print("Bot successfully shut down")
            sys.exit(0)

        @self.tree.command(name="bumbot-online", description="Check to see if bumbot is online.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def bumbot_online(interaction: discord.Interaction):
            await interaction.response.send_message("TGO MMO - Online ✔", delete_after=5)
            return True

        @self.tree.command(name="bumbot-test", description="A test function. Does whatever I need it to for whenever I need it.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def bumbot_test(interaction: discord.Interaction):
            get_tgommo_db_handler().get_active_collections(convert_to_object=True)

            await interaction.message.delete()
            return True

    def register_misc_feature_commands(self):
        @self.tree.command(name="get-user-profile-pic", description="Display a user's profile picture by user ID.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def get_user_profile_pic(interaction: discord.Interaction, user_id: str = None):
            target_user = interaction.guild.get_member(interaction.user.id if user_id is None else int(user_id))
            profile_pic_url = get_user_discord_profile_pic(target_user)

            # Create an embed with the avatar
            embed = discord.Embed(title=f"{target_user.name}'s Avatar")
            embed.set_image(url=profile_pic_url)

            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="shiny-check", description="Check how many messages its been since the last shiny.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def shiny_check(interaction):
            await interaction.response.send_message(f"Its been {get_game_state_manager().get_shiny_message_count()} messages since the last shiny", delete_after=60)

    def register_tgommo_user_general_commands(self):
        @self.tree.command(name="current-environment-tgommo", description="Displays the current TGOMMO environment.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_current_environment(interaction: discord.Interaction):
            await interaction.response.send_message(f"Current Environment: {self.creature_spawner_handler.current_environment.name} ({self.creature_spawner_handler.time_of_day})", delete_after=10)

    def register_tgommo_user_navigation_commands(self):
        @self.tree.command(name="tgommo", description="Brings up the master menu for TGOMMO.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_menu(interaction):
            from src.discord.game_features.TGOMMOMenuView import TGOMMOMenuView
            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id)

            view = TGOMMOMenuView(message_author=message_author, target_user=message_author, discord_bot=self)

            await interaction.response.send_message(f'{interaction.user.mention} Welcome to the TGO MMO Help Menu!', files=[], view=view)

        @self.tree.command(name="open-avatar-board-tgommo", description="Opens User's Avatar Quest & Collection Board.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_open_avatar_board(interaction, user_id: str = None):
            await interaction.response.defer()

            target_user_id = int(user_id) if user_id and user_id.isdigit() else interaction.user.id
            target_user = get_tgommo_db_handler().get_user_profile_by_user_id(target_user_id)
            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id)

            avatar_board_image_factory = AvatarBoardImageFactory(message_author=message_author, target_user=target_user)
            view = AvatarBoardView(message_author=message_author, target_user= target_user, avatar_board_image_factory=avatar_board_image_factory)

            await interaction.followup.send('', files=[view.reload_image()], view=view)

        @self.tree.command(name="open-creature-inventory-tgommo", description="Opens User's Creature Inventory.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_open_creature_inventory(interaction, user_id: str = None):
            await interaction.response.defer()

            target_user_id = int(user_id) if user_id and user_id.isdigit() else interaction.user.id
            target_user = get_tgommo_db_handler().get_user_profile_by_user_id(target_user_id)
            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id)

            creature_inventory_image_factory = CreatureInventoryImageFactory(message_author=message_author, target_user=target_user)
            view = CreatureInventoryView(message_author=message_author, target_user=target_user, creature_inventory_image_factory=creature_inventory_image_factory)

            await interaction.followup.send(content='', files=[view.reload_image()], view=view)

        @self.tree.command(name="open-encyclopedia-tgommo", description="Opens User's Encyclopedia.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_open_encyclopedia(interaction, user_id: str = None):
            await interaction.response.defer()

            target_user_id = int(user_id) if user_id and user_id.isdigit() else interaction.user.id
            target_user = get_tgommo_db_handler().get_user_profile_by_user_id(target_user_id)
            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id)

            encyclopedia_location_index_img_factory = EncyclopediaLocationIndexImageFactory(message_author=message_author, target_user=target_user,)
            view = EncyclopediaLocationIndexView(message_author=message_author, target_user=target_user, encyclopedia_location_index_image_factory=encyclopedia_location_index_img_factory, )

            await interaction.followup.send('', files=[view.reload_image()], view=view)

        @self.tree.command(name="open-item-inventory-tgommo", description="Opens User's Item Inventory.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_open_item_inventory(interaction):
            await interaction.response.defer()

            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=interaction.user.id)
            target_user = message_author

            item_inventory_handler = ItemInventoryImageFactory(message_author=message_author, target_user=target_user,)
            view = ItemInventoryView(message_author=message_author, target_user=target_user, item_inventory_image_factory=item_inventory_handler, discord_bot=self)

            await interaction.followup.send(files=[view.reload_image()], view=view)

        @self.tree.command(name="open-player_profile-tgommo", description="Opens User's Player Profile.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_open_player_profile(interaction, user_id: str = None):
            await interaction.response.defer()

            user_id = int(user_id) if user_id and user_id.isdigit() else interaction.user.id
            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id)
            target_user = get_tgommo_db_handler().get_user_profile_by_user_id(user_id)

            player_profile_image_factory = PlayerProfileImageFactory(message_author= message_author, target_user=target_user)
            view = PlayerProfileView(message_author=get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id), target_user=get_tgommo_db_handler().get_user_profile_by_user_id(user_id), player_profile_image_factory=player_profile_image_factory)


            await interaction.followup.send('', files=[view.reload_image()], view=view)

        @self.tree.command(name="open-morshus-shop-tgommo", description="Opens Morshu's Shop.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_open_shop(interaction):
            await interaction.response.defer()

            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id)

            shop_image_factory = ShopImageFactory(message_author=message_author)
            view = ShopView(message_author=message_author, shop_image_factory=shop_image_factory)

            await interaction.followup.send(files=[view.reload_image()], view=view)

        @self.tree.command(name="open-trap-manager", description="Opens the Trap Manager.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_open_shop(interaction):
            await interaction.response.defer()

            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id)

            trap_manager_image_factory = TrapManagerImageFactory(message_author=message_author)
            trap_manager_view = TrapManagerView(message_author=message_author, trap_manager_image_factory=trap_manager_image_factory)

            await interaction.followup.send(files=[trap_manager_view.reload_image()], view=trap_manager_view)

    def register_tgommo_admin_commands(self):
        @admin_only()
        @self.tree.command(name="spawn_creature_tgommo", description="Manually spawn a creature. Admins Only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_spawn_creature(interaction, creature_id:int = None, environment_id:int=None, is_mythical: str = None):
            creature = get_tgommo_db_handler().get_environment_creature_by_environment_id_and_creature_id(creature_id=creature_id, environment_id=environment_id) if creature_id else await self.creature_spawner_handler.creature_picker()
            if creature_id and not creature:
                await interaction.response.send_message(f"Invalid creature combination: creature_id {creature_id} not found in environment_id {environment_id}", delete_after=10, ephemeral=True)
                return

            creature.set_creature_rarity(MYTHICAL) if is_mythical else None

            await self.creature_spawner_handler.spawn_creature(creature=creature)
            await interaction.response.send_message(f"Manually spawned a {creature.name}", delete_after=5)

        @admin_only()
        @self.tree.command(name="spawn_every_creature_tgommo", description="Spawns one of every creature for a given environment.  Admins Only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_spawn_every_creature(interaction, environment_dex_no: str = None, environment_id: str = None, is_mythical: str = None,):

            if not environment_id and not environment_dex_no:
                await interaction.response.send_message(f"Please provide either an environment dex number or environment ID to spawn creatures.", delete_after=10, ephemeral=True)
                return

            environment = get_tgommo_db_handler().get_environments_by_dex_no(dex_no=environment_dex_no)[0] if environment_dex_no else get_tgommo_db_handler().get_environment_by_id(environment_id=environment_id)
            spawn_pool = get_tgommo_db_handler().get_creatures_for_environment_by_dex_no(dex_no=environment.dex_no) if environment_dex_no else get_tgommo_db_handler().get_creatures_for_environment_by_environment_id(environment_id=environment_id)

            await interaction.response.send_message(f"Spawning all creatures for {environment.name}", delete_after=5, ephemeral=True)
            for creature in spawn_pool:
                if is_mythical:
                    creature.set_rarity(MYTHICAL)

                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        await self.creature_spawner_handler.spawn_creature(creature=creature)
                        await interaction.channel.send(f"Manually spawned a {creature.name}", delete_after=5)
                        break  # Success, exit retry loop
                    except (discord.errors.HTTPException, aiohttp.ClientOSError) as e:
                        if attempt < max_retries - 1:
                            print(f"Network error when spawning {creature.name}: {e}. Retrying...")
                            await asyncio.sleep(2)  # Wait before retrying
                        else:
                            await interaction.channel.send(f"Failed to spawn {creature.name} after {max_retries} attempts.", delete_after=5)

        @admin_only()
        @self.tree.command(name='toggle_creature_spawns_tgommo', description="Turn creature spawns on / off.  Admins Only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def toggle_creature_spawns(interaction):
            result = self.creature_spawner_handler.toggle_creature_spawner(interaction)
            await interaction.response.send_message(result, delete_after=5)

        @admin_only()
        @self.tree.command(name="change_environment_tgommo", description="Change the current TGOMMO environment. Admins Only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        @discord.app_commands.describe(environment_dex_no="Environment dex number (leave empty for random)")
        async def tgommo_change_environment(interaction, environment_dex_no: int = None):
            try:
                if environment_dex_no:
                    new_environment = get_tgommo_db_handler().get_environment_by_dex_no_and_variant_no(dex_no=environment_dex_no, variant_no=self.creature_spawner_handler.current_environment.variant_no)
                else:
                    new_environment = get_tgommo_db_handler().get_random_environment_in_rotation(is_night_environment=0 if self.creature_spawner_handler.is_day else 1, convert_to_object=True)

                if not new_environment:
                    await interaction.response.send_message(f"Environment with dex number {environment_dex_no} not found.", delete_after=10, ephemeral=True)
                    return
                self.creature_spawner_handler.define_environment_and_spawn_pool(environment_dex_no=new_environment.dex_no, environment_variant_no=new_environment.variant_no)

                # Announce the environment change in the spawn channel
                await interaction.response.send_message(f"Environment changed to: {new_environment.name} (Dex No: {environment_dex_no})", delete_after=10)
                await self.get_channel(TGOMMO_CREATURE_SPAWN_CHANNEL_ID).send(f"\n\n# __⚠️✈️ **Travel Advisory** ✈️⚠️__ \nEnvironment Changed! Now exploring:\n## **🌍 {new_environment.name}** 🌍", files=[convert_to_png(Image.open(f"{TGOMMO_TRAVEL_ADVISORY_LANDING_BASE}{new_environment.dex_no}{IMAGE_FILE_EXTENSION}"), file_name=f"travel_advisory_image.png")])
            except Exception as e:
                await interaction.response.send_message(f"Error changing environment: {str(e)}", delete_after=10, ephemeral=True)

        @admin_only()
        @self.tree.command(name="refresh_shop_tgommo", description="Manually refresh the daily shop. Admins Only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_ID))
        async def tgommo_refresh_shop(interaction):
            try:
                await interaction.response.defer(ephemeral=True)

                # Manually trigger the shop refresh
                await self.shop_restock_scheduler.refresh_daily_shop()
                await interaction.followup.send("Shop has been manually refreshed!", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Error refreshing shop: {str(e)}", ephemeral=True)


    '''---- TEST COMMANDS ----------------------------------------------------------------------------------------------------'''
    def register_test_commands(self):
        register_general_tests(self)

        # GAME FEATURE TESTS
        register_creature_encounter_tests(self)
        register_shop_tests(self)
        register_encyclopedia_tests(self)

    def start_bot(self):
        self.run(self.token)

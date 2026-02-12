import asyncio
import sys

import aiohttp
import discord
from discord.ext import commands
from pyexpat.errors import messages

from src.commons.CommonFunctions import get_user_discord_profile_pic, admin_only, convert_to_png
from src.commons.GuildHandler import set_guild
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarBoardImageFactory import AvatarBoardImageFactory
from src.discord.game_features.avatar_board.AvatarBoardView import AvatarBoardView
from src.discord.game_features.creature_enounter.CreatureSpawnerHandler import CreatureSpawnerHandler
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.creature_inventory.CreatureInventoryView import CreatureInventoryView
from src.discord.game_features.encyclopedia_location_index.EncyclopediaLocationIndexImageFactory import \
    EncyclopediaLocationIndexImageFactory
from src.discord.game_features.encyclopedia_location_index.EncyclopediaLocationIndexView import \
    EncyclopediaLocationIndexView
from src.discord.game_features.item_inventory.ItemInventoryImageFactory import ItemInventoryImageFactory
from src.discord.game_features.item_inventory.ItemInventoryView import ItemInventoryView
from src.discord.game_features.player_profile.PlayerProfileImageFactory import PlayerProfileImageFactory
from src.discord.game_features.player_profile.PlayerProfileView import PlayerProfileView
from src.discord.objects.CreatureRarity import MYTHICAL
from src.resources.constants.general_constants import TGOMMO_ACTIVE_SERVER_TOKEN


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

        self.creature_spawner_handler = CreatureSpawnerHandler(self)

    ''' EVENTS '''
    def register_events(self):
        @self.event
        async def on_ready():
            print(f'DiscordBot - Logged in as {self.user.name} ({self.user.id})')

            try:
                set_guild(self)
                print(f"Synced {len(await self.tree.sync(guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN)))} command(s) to guild")
            except Exception as e:
                print(f"Failed to sync commands: {e}")

            self.creature_spawner_handler.start_creature_spawner()

        @self.event
        async def on_command_error(ctx, error):
            if isinstance(error, discord.ext.commands.CommandNotFound):
                # Silently ignore command not found errors
                return
            # Re-raise other errors so they aren't suppressed
            raise error

    ''' COMMANDS '''
    def register_core_commands(self):
        @self.tree.command(name="shutdown", description="Completely shuts down bumbot. Please for emergencies only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def shutdown(interaction: discord.Interaction):
            print("Shutting down bot...")
            await interaction.response.send_message("Successfully shut down bot.", delete_after=5)

            # Close the Discord connection
            if self:
                await self.close()

            print("Bot successfully shut down")
            sys.exit(0)

        @self.tree.command(name="bumbot-online", description="Check to see if bumbot is online.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def bumbot_online(interaction: discord.Interaction):
            await interaction.response.send_message("TGO MMO - Online ✔", delete_after=5)
            return True

        @self.tree.command(name="bumbot-test", description="A test function. Does whatever I need it to for whenever I need it.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def bumbot_test(interaction: discord.Interaction):
            get_tgommo_db_handler().get_active_collections(convert_to_object=True)

            await interaction.message.delete()
            return True

    def register_misc_feature_commands(self):
        @self.tree.command(name="get-user-profile-pic", description="Display a user's profile picture by user ID.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def get_user_profile_pic(interaction: discord.Interaction, user_id: str = None):
            target_user = interaction.guild.get_member(interaction.user.id if user_id is None else int(user_id))
            profile_pic_url = get_user_discord_profile_pic(target_user)

            # Create an embed with the avatar
            embed = discord.Embed(title=f"{target_user.name}'s Avatar")
            embed.set_image(url=profile_pic_url)

            await interaction.response.send_message(embed=embed)

    def register_tgommo_user_general_commands(self):
        @self.tree.command(name="current-environment-tgommo", description="Displays the current TGOMMO environment.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def tgommo_current_environment(interaction: discord.Interaction):
            env = self.creature_spawner_handler.current_environment
            await interaction.response.send_message(f"Current Environment: {env.name} ({self.creature_spawner_handler.time_of_day})", delete_after=10)

    def register_tgommo_user_navigation_commands(self):
        @self.tree.command(name="tgommo", description="Brings up the master menu for TGOMMO.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def tgommo_menu(interaction):
            from src.discord.game_features.TGOMMOMenuView import TGOMMOMenuView
            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id)

            await interaction.response.send_message(f'{interaction.user.mention} Welcome to the TGO MMO Help Menu!', files=[], view=TGOMMOMenuView(message_author=message_author, target_user=message_author, discord_bot=self))

        @self.tree.command(name="open-avatar-board-tgommo", description="Opens User's Avatar Quest & Collection Board.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def tgommo_open_avatar_board(interaction, user_id: str = None):
            user_id = int(user_id) if user_id and user_id.isdigit() else interaction.user.id

            avatar_board_handler = AvatarBoardImageFactory(user_id=user_id)
            avatar_board_img = avatar_board_handler.build_avatar_board_page_image()
            view = AvatarBoardView(message_author=interaction.user, avatar_board_image_factory=avatar_board_handler)

            await interaction.response.send_message('', files=[convert_to_png(avatar_board_img, f'avatar_board.png')], view=view)

        @self.tree.command(name="open-creature-inventory-tgommo", description="Opens User's Creature Inventory.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def tgommo_open_creature_inventory(interaction, user_id: str = None):
            target_user = interaction.guild.get_member(int(user_id) if user_id and user_id.isdigit() else interaction.user.id)

            creature_inventory_handler = CreatureInventoryImageFactory(user=target_user)
            view = CreatureInventoryView(message_author=interaction.user, target_user=target_user.id, creature_inventory_image_factory=creature_inventory_handler)

            await interaction.response.send_message(content='', files=[convert_to_png(creature_inventory_handler.get_creature_inventory_page_image(), f'avatar_board.png')], view=view)

        @self.tree.command(name="open-encyclopedia-tgommo", description="Opens User's Encyclopedia.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def tgommo_open_encyclopedia(interaction, user_id: str = None):
            user_id = user_id if user_id and (user_id.lower() == "server" or user_id.isdigit()) else interaction.user.id
            target_user = None if user_id == "server" else interaction.guild.get_member(int(user_id))

            encyclopedia_location_index_img_factory = EncyclopediaLocationIndexImageFactory(user=target_user, )
            view = EncyclopediaLocationIndexView(message_author=interaction.user, target_user=target_user, encyclopedia_location_index_image_factory=encyclopedia_location_index_img_factory, )

            await interaction.response.send_message('', files=[convert_to_png(encyclopedia_location_index_img_factory.build_encyclopedia_location_index_page_image(), f'encyclopedia_location_index.png')], view=view)

        @self.tree.command(name="open-item-inventory-tgommo", description="Opens User's Item Inventory.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def tgommo_open_item_inventory(interaction):
            target_user = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=interaction.user.id)

            item_inventory_handler = ItemInventoryImageFactory(user=target_user, )
            view = ItemInventoryView(message_author=target_user, target_user=target_user, item_inventory_image_factory=item_inventory_handler, discord_bot=self)

            await interaction.response.send_message(files=[convert_to_png(item_inventory_handler.generate_item_inventory_image(), f'avatar_board.png')], view=view)

        @self.tree.command(name="open-player_profile-tgommo", description="Opens User's Player Profile.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def tgommo_open_player_profile(interaction, user_id: str = None):
            user_id = int(user_id) if user_id and user_id.isdigit() else interaction.user.id

            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id)
            target_user = get_tgommo_db_handler().get_user_profile_by_user_id(user_id)

            player_profile_image_factory = PlayerProfileImageFactory(message_author= message_author, target_user=target_user)
            view = PlayerProfileView(message_author=get_tgommo_db_handler().get_user_profile_by_user_id(interaction.user.id), target_user=get_tgommo_db_handler().get_user_profile_by_user_id(user_id), player_profile_image_factory=player_profile_image_factory)
            await interaction.response.send_message('', files=[view.reload_image()], view=view)

    def register_tgommo_admin_commands(self):
        @admin_only()
        @self.tree.command(name="spawn_creature_tgommo", description="Manually spawn a creature. Admins Only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def tgommo_spawn_creature(interaction, creature_id:int = None, environment_id:int=None, is_mythical: str = None):
            creature = get_tgommo_db_handler().get_environment_creature_by_environment_id_and_creature_id(creature_id=creature_id, environment_id=environment_id) if creature_id else await self.creature_spawner_handler.creature_picker()
            if creature_id and not creature:
                await interaction.response.send_message(f"Invalid creature combination: creature_id {creature_id} not found in environment_id {environment_id}", delete_after=10, ephemeral=True)
                return

            creature.set_creature_rarity(MYTHICAL) if is_mythical else None

            await self.creature_spawner_handler.spawn_creature(creature=creature)
            await interaction.response.send_message(f"Manually spawned a {creature.name}", delete_after=5)

        @admin_only()
        @self.tree.command(name="spawn_every_creature_tgommo", description="Spawns one of every creature for a given environment.  Admins Only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
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
                        await interaction.response.send_message(f"Manually spawned a {creature.name}", delete_after=5)
                        break  # Success, exit retry loop
                    except (discord.errors.HTTPException, aiohttp.ClientOSError) as e:
                        if attempt < max_retries - 1:
                            print(f"Network error when spawning {creature.name}: {e}. Retrying...")
                            await asyncio.sleep(2)  # Wait before retrying
                        else:
                            await interaction.channel.send(f"Failed to spawn {creature.name} after {max_retries} attempts.", delete_after=5)

        @admin_only()
        @self.tree.command(name='toggle_creature_spawns_tgommo', description="Turn creature spawns on / off.  Admins Only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def toggle_creature_spawns(interaction):
            result = self.creature_spawner_handler.toggle_creature_spawner(interaction)
            await interaction.response.send_message(result, delete_after=5)

        @admin_only()
        @self.tree.command(name="change_environment_tgommo", description="Change the current TGOMMO environment. Admins Only.", guild=discord.Object(id=TGOMMO_ACTIVE_SERVER_TOKEN))
        async def tgommo_change_environment(interaction, environment_dex_no: int):
            try:
                environment = get_tgommo_db_handler().get_environment_by_dex_no_and_variant_no(dex_no=environment_dex_no, variant_no=self.creature_spawner_handler.current_environment.variant_no)
                if not environment:
                    await interaction.response.send_message(f"Environment with dex number {environment_dex_no} not found.", delete_after=10, ephemeral=True)
                    return
                self.creature_spawner_handler.current_environment = environment

                await interaction.response.send_message(
                    f"Environment changed to: {environment.name} (Dex No: {environment_dex_no})", delete_after=10)

            except Exception as e:
                await interaction.response.send_message(f"Error changing environment: {str(e)}", delete_after=10, ephemeral=True)

    def start_bot(self):
        self.run(self.token)
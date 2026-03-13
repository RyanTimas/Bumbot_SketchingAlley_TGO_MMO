import discord
from PIL import Image

from src.commons.CommonFunctions import convert_to_png, interaction_guard
from src.commons.CommonFunctions import retry_on_ssl_error
from src.commons.CommonViewComponents import create_dummy_label_button
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.DiscordBot import DiscordBot
from src.discord.game_features.avatar_board.AvatarBoardAvatarQuestImageFactory import AvatarBoardAvatarQuestImageFactory
from src.discord.game_features.avatar_board.AvatarBoardImageFactory import AvatarBoardImageFactory
from src.discord.game_features.avatar_board.AvatarBoardUnlockedAvatarImageFactory import AvatarBoardUnlockedAvatarImageFactory
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.creature_inventory.CreatureInventoryView import CreatureInventoryView
from src.discord.game_features.avatar_board.AvatarBoardView import AvatarBoardView
from src.discord.game_features.encyclopedia_location_index.EncyclopediaLocationIndexImageFactory import EncyclopediaLocationIndexImageFactory
from src.discord.game_features.encyclopedia_location_index.EncyclopediaLocationIndexView import EncyclopediaLocationIndexView
from src.discord.game_features.item_inventory.ItemInventoryImageFactory import ItemInventoryImageFactory
from src.discord.game_features.item_inventory.ItemInventoryView import ItemInventoryView
from src.discord.game_features.player_profile.PlayerProfileView import PlayerProfileView
from src.discord.game_features.player_profile.PlayerProfileImageFactory import PlayerProfileImageFactory, PLAYER_PROFILE_TAB_OPEN_TEAM
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.file_paths import *

server_encyclopedia_button_name = "server_encyclopedia"
user_encyclopedia_button_name = "user_encyclopedia"

class TGOMMOMenuView(BaseView):
    def __init__(self, message_author, target_user, discord_bot: DiscordBot):
        super().__init__(message_author=message_author, target_user=target_user)
        self.discord_bot = discord_bot

        # Initialize view buttons
        self.welcome_button = self.create_welcome_button()
        self.help_button = self.create_help_button()

        # todo: removed for now and can add back in later if needed, just wanted to test out the look of the menu without it
        # self.dummy_encyclopedia_label_button = create_dummy_label_button(label_text="Encyclopedia Page: ", row=1)
        # self.open_server_encyclopedia_button = self.create_encyclopedia_button(server_encyclopedia_button_name, 1)

        self.open_user_encyclopedia_button = self.create_encyclopedia_button(user_encyclopedia_button_name, 1)
        self.open_player_profile_button = self.create_player_profile_button(tab_is_open=False, open_tab=PLAYER_PROFILE_TAB_OPEN_TEAM, row=1)

        self.avatar_board_button = self.create_avatar_board_button(row=2)
        self.creature_inventory_button = self.create_creature_inventory_button(row=2)
        self.item_inventory_button = self.create_item_inventory_button(row=2)

        # Update button states
        self.refresh_view()

    # CREATE BUTTONS
    # Open Screen Buttons
    def create_encyclopedia_button(self, button_type, row=1):
        button_data = {
            user_encyclopedia_button_name: ["User", discord.ButtonStyle.blurple, None],
            server_encyclopedia_button_name: ["Server", discord.ButtonStyle.blurple, None],
        }
        label, style, emojii = button_data[button_type]
        button = discord.ui.Button(label="Creature Encyclopedia", style=style, emoji=emojii, row=row, custom_id=f"encyclopedia_{button_type}")
        button.callback = self.encyclopedia_callback(button_type=button_type)
        return button
    def encyclopedia_callback(self, button_type):
        @interaction_guard(self)
        async def callback(interaction):
            server_user = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=0)

            encyclopedia_location_index_img_factory = EncyclopediaLocationIndexImageFactory(message_author=self.message_author, target_user=self.target_user if button_type == "user_encyclopedia" else server_user, )
            view = EncyclopediaLocationIndexView(message_author=self.message_author, target_user=self.target_user if button_type == "user_encyclopedia" else server_user, encyclopedia_location_index_image_factory=encyclopedia_location_index_img_factory, original_view=self)

            # view.update_button_states()
            await interaction.message.edit(attachments=[convert_to_png(encyclopedia_location_index_img_factory.reload_image(), f'encyclopedia_location_index_page.png')], view=view)
        return callback

    def create_player_profile_button(self, tab_is_open=False, open_tab=PLAYER_PROFILE_TAB_OPEN_TEAM, row=1):
        button = discord.ui.Button(label="Player Profile", style=discord.ButtonStyle.blurple, row=row)
        button.callback = self.player_profile_callback(tab_is_open=tab_is_open, open_tab=open_tab)
        return button
    def player_profile_callback(self, tab_is_open=False, open_tab=PLAYER_PROFILE_TAB_OPEN_TEAM):
        @interaction_guard(self)
        async def callback(interaction):
            player_profile_img_factory = PlayerProfileImageFactory(message_author=self.message_author, target_user=self.target_user)
            view = PlayerProfileView(message_author=self.message_author, target_user=self.message_author, player_profile_image_factory=player_profile_img_factory, tab_is_open=tab_is_open, open_tab=open_tab, original_view=self)

            await interaction.message.edit(attachments=[view.reload_image()], view=view)
        return callback

    def create_avatar_board_button(self, row=1):
        button = discord.ui.Button(label="Open Avatar Board", style=discord.ButtonStyle.green, row=row)
        button.callback = self.display_avatar_board_callback()
        return button
    def display_avatar_board_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            avatar_board_img_factory = AvatarBoardImageFactory(message_author=self.message_author, target_user=self.target_user)
            avatar_board_view = AvatarBoardView(message_author=self.message_author, target_user=self.target_user, avatar_board_image_factory=avatar_board_img_factory, original_view=self, )

            await interaction.message.edit(attachments=[convert_to_png(avatar_board_img_factory.build_image(), f'avatar_board.png')], view=avatar_board_view)
        return callback

    def create_creature_inventory_button(self, row=1):
        button = discord.ui.Button(label="Open Creature Inventory", style=discord.ButtonStyle.green, row=row)
        button.callback = self.creature_inventory_callback()  # Add parentheses to call the function
        return button
    def creature_inventory_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            creature_inventory_img_factory = CreatureInventoryImageFactory(message_author=self.message_author, target_user=self.target_user)
            creature_inventory_view = CreatureInventoryView(message_author=self.message_author, target_user=self.target_user, creature_inventory_image_factory=creature_inventory_img_factory, original_view=self)

            await interaction.message.edit(attachments=[convert_to_png(creature_inventory_img_factory.reload_image(), f'creature_inventory_img.png')], view=creature_inventory_view)

        return callback

    def create_item_inventory_button(self, row=1):
        button = discord.ui.Button(label="Open Item Inventory", style=discord.ButtonStyle.green, row=row)
        button.callback = self.item_inventory_callback()
        return button
    def item_inventory_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            item_inventory_img_factory = ItemInventoryImageFactory(message_author=self.message_author, target_user=self.target_user)
            item_inventory_view = ItemInventoryView(message_author=self.message_author, target_user=self.target_user, item_inventory_image_factory=item_inventory_img_factory, original_message=interaction.message, original_view=self, discord_bot=self.discord_bot)

            await interaction.message.edit(attachments=[convert_to_png(item_inventory_img_factory.reload_image(), f'item_inventory_img.png')], view=item_inventory_view)
        return callback

    def create_welcome_button(self):
        button = discord.ui.Button(label="What is TGO MMO?", style=discord.ButtonStyle.gray, row=0)
        button.callback = self.welcome_callback()
        return button
    def welcome_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()
                await interaction.followup.send(files=[convert_to_png(Image.open(HELP_IMAGE_WELCOME_CARD_INTRO), f'welcome_img_1.png')], ephemeral=True)
                await interaction.followup.send(files=[convert_to_png(Image.open(HELP_IMAGE_WELCOME_CARD_HOW_TO_PLAY), f'welcome_img_2.png')], ephemeral=True)
                await interaction.followup.send(files=[convert_to_png(Image.open(HELP_IMAGE_WELCOME_CARD_RARITY_SYSTEM), f'welcome_img_3.png')], ephemeral=True)
                await interaction.followup.send(files=[convert_to_png(Image.open(HELP_IMAGE_WELCOME_CARD_FUTURE_UPDATES), f'welcome_img_4.png')], ephemeral=True)
        return callback

    def create_help_button(self):
        button = discord.ui.Button(label="Help & Commands", style=discord.ButtonStyle.gray, row=0)
        button.callback = self.help_callback()
        return button
    def help_callback(self):
        async def callback(interaction):
            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                # Load help images
                welcome_img = Image.open(HELP_IMAGE_WELCOME_CARD)
                button_img = Image.open(HELP_IMAGE_BUTTON_CARD)
                command_img_1 = Image.open(HELP_IMAGE_COMMAND_CARD_1)
                command_img_2 = Image.open(HELP_IMAGE_COMMAND_CARD_2)
                if get_tgommo_db_handler().get_total_mythical_catches_for_server() > 0:
                    command_img_2_mythic_addon = Image.open(HELP_IMAGE_COMMAND_CARD_2_MYTHIC_ADDON)
                    command_img_2.paste(command_img_2_mythic_addon, (0, 0), command_img_2_mythic_addon)

                # Send help images
                await interaction.followup.send(files=[convert_to_png(welcome_img, f'welcome_img.png')], ephemeral=True)
                await interaction.followup.send(files=[convert_to_png(button_img, f'welcome_img.png')], ephemeral=True)
                await interaction.followup.send(files=[convert_to_png(command_img_1, f'welcome_img.png')], ephemeral=True)
                await interaction.followup.send(files=[convert_to_png(command_img_2, f'welcome_img.png')], ephemeral=True)
        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def rebuild_view(self):
        super().rebuild_view()
        
        # Create view layout
        self.add_item(self.welcome_button)
        # self.add_item(self.help_button)

        # self.add_item(self.dummy_encyclopedia_label_button)
        self.add_item(self.open_user_encyclopedia_button)
        # self.add_item(self.open_server_encyclopedia_button)
        self.add_item(self.open_player_profile_button)

        self.add_item(self.avatar_board_button)
        self.add_item(self.creature_inventory_button)
        self.add_item(self.item_inventory_button)

        self.remove_item(self.change_user_button)


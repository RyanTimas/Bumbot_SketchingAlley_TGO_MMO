import asyncio

import discord
from PIL import Image

from src.commons.CommonFunctions import convert_to_png
from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view, \
    create_dummy_label_button
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.DiscordBot import DiscordBot
from src.discord.buttonhandlers.EncyclopediaView import EncyclopediaView
from src.discord.image_factories.EncyclopediaImageFactory import EncyclopediaImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class TGOMMOMenuView(discord.ui.View):
    def __init__(self, message_author, discord_bot: DiscordBot):
        super().__init__(timeout=None)

        self.message_author = message_author
        self.discord_bot = discord_bot

        # Add a lock to prevent concurrent button interactions
        self.interaction_lock = asyncio.Lock()

        # Initialize button names
        server_encyclopedia_button_name = "server_encyclopedia"
        user_encyclopedia_button_name = "user_encyclopedia"

        # Add a button to open input modal

        # Initialize view buttons
        self.help_button = self.create_help_button()

        self.open_user_encyclopedia_button = self.create_encyclopedia_button(user_encyclopedia_button_name, 1)
        self.open_server_encyclopedia_button = self.create_encyclopedia_button(server_encyclopedia_button_name, 1)

        self.close_button = self.create_close_button(row=3)

        # Create view layout
        self.add_item(self.help_button)

        self.add_item(create_dummy_label_button(label_text="Encyclopedia Page: ", row=1))
        self.add_item(self.open_user_encyclopedia_button)
        self.add_item(self.open_server_encyclopedia_button)

        self.add_item(self.close_button)

        # Update button states
        self.update_button_states()


    # Handle Encyclopedia Buttons - opens encyclopedia view
    def create_encyclopedia_button(self, button_type, row=1):
        labels = {
            "user_encyclopedia": "User",
            "server_encyclopedia": "Server",
        }
        styles = {
            "user_encyclopedia": discord.ButtonStyle.blurple,
            "server_encyclopedia": discord.ButtonStyle.green,
        }
        emojis = {
            "user_encyclopedia": None,
            "server_encyclopedia": None
        }


        button = discord.ui.Button(
            label=labels[button_type],
            style=styles[button_type],
            emoji=emojis[button_type],
            row=row
        )
        button.callback = self.encyclopedia_callback(button_type=button_type, is_verbose=False, show_variants=False, show_mythics=False)
        return button

    def encyclopedia_callback(self, button_type, is_verbose=False, show_variants=False, show_mythics=False):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                encyclopedia_img_factory = EncyclopediaImageFactory(
                    user=self.message_author,
                    environment=self.discord_bot.creature_spawner_handler.current_environment,
                    verbose=is_verbose,
                    is_server_page=button_type == "server_encyclopedia",
                    show_variants=show_variants,
                    show_mythics=show_mythics
                )

                view = EncyclopediaView(
                    encyclopedia_image_factory=encyclopedia_img_factory,
                    is_verbose=is_verbose,
                    show_variants=show_variants,
                    show_mythics=show_mythics,
                    message_author=self.message_author
                )

                # Update button states
                self.update_button_states()

                new_encyclopedia_page = encyclopedia_img_factory.build_encyclopedia_page_image()
                file = convert_to_png(new_encyclopedia_page, f'encyclopedia_page.png')

                # Send updated view
                await interaction.message.edit(attachments=[file], view=view)

        return callback


    # Handle Encyclopedia Buttons - opens encyclopedia view
    def create_welcome_button(self):
        button = discord.ui.Button(
            label="What is TGO MMO?",
            style=discord.ButtonStyle.red,
            row=0
        )
        button.callback = self.welcome_callback()
        return button

    def welcome_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                return

        return callback



    def create_help_button(self):
        button = discord.ui.Button(
            label="Help",
            style=discord.ButtonStyle.red,
            row=0
        )
        button.callback = self.help_callback()
        return button

    def help_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                # Load help images
                welcome_img = Image.open(HELP_IMAGE_WELCOME_CARD)
                button_img = Image.open(HELP_IMAGE_BUTTON_CARD)
                command_img_1 = Image.open(HELP_IMAGE_COMMAND_CARD_1)
                command_img_2 = Image.open(HELP_IMAGE_COMMAND_CARD_2)
                if get_tgommo_db_handler().get_server_mythical_count() > 0:
                    command_img_2_mythic_addon = Image.open(HELP_IMAGE_COMMAND_CARD_2_MYTHIC_ADDON)
                    command_img_2.paste(command_img_2_mythic_addon, (0, 0), command_img_2_mythic_addon)

                # Send help images
                await interaction.followup.send(files=[convert_to_png(welcome_img, f'welcome_img.png')], ephemeral=True)
                await interaction.followup.send(files=[convert_to_png(button_img, f'welcome_img.png')], ephemeral=True)
                await interaction.followup.send(files=[convert_to_png(command_img_1, f'welcome_img.png')], ephemeral=True)
                await interaction.followup.send(files=[convert_to_png(command_img_2, f'welcome_img.png')], ephemeral=True)

                # Send help text messages (unused)
                # mythics_unlocked = get_tgommo_db_handler().get_server_mythical_count() > 0
                # help_text_header = (
                #     TGOMMO_HELP_MENU_TITLE
                # )
                # help_text_buttons = (
                #     TGOMMO_HELP_MENU_BUTTON_DESCRIPTION
                #     + TGOMMO_HELP_MENU_BUTTON_OPTIONS
                # )
                # help_text_commands = (
                #     TGOMMO_HELP_MENU_COMMANDS_DESCRIPTION_1
                #     + TGOMMO_HELP_MENU_COMMANDS_OPTIONS_1
                #     + TGOMMO_HELP_MENU_COMMANDS_DESCRIPTION_2
                #     + TGOMMO_HELP_MENU_COMMANDS_OPTIONS_2 if mythics_unlocked else ""
                #
                #     + TGOMMO_HELP_MENU_FOOTER
                # )
                #
                # await interaction.followup.send(help_text_header, ephemeral=True)
                # await interaction.followup.send(help_text_buttons, ephemeral=True)
                # await interaction.followup.send(help_text_commands, ephemeral=True)

        return callback


    # Handle Close Button
    def create_close_button(self, row=2):
        button = discord.ui.Button(
            label="✘",
            style=discord.ButtonStyle.red,
            row=row,
        )
        button.callback = self.close_callback()
        return button

    def close_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            # For delete operation, we need a shorter lock
            async with self.interaction_lock:
                # Delete the message
                await interaction.message.delete()

        return callback


    def update_button_states(self):
        return


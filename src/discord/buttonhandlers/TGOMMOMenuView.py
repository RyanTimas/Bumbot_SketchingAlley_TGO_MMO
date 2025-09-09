import asyncio

import discord

from src.commons.CommonFunctions import convert_to_png
from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view, \
    create_dummy_label_button
from src.discord.DiscordBot import DiscordBot
from src.discord.buttonhandlers.EncyclopediaView import EncyclopediaView
from src.discord.image_factories.EncyclopediaImageFactory import EncyclopediaImageFactory


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
        self.add_item(create_dummy_label_button(label_text="Open Encyclopedia Page: ", row=1))
        self.open_user_encyclopedia_button = self.create_encyclopedia_button(user_encyclopedia_button_name, 1)
        self.open_server_encyclopedia_button = self.create_encyclopedia_button(server_encyclopedia_button_name, 1)

        self.close_button = self.create_close_button()

        # Add buttons to view
        self.add_item(self.help_button)

        self.add_item(self.open_server_encyclopedia_button)
        self.add_item(self.open_user_encyclopedia_button)

        self.add_item(self.close_button)

        # Update button states
        self.update_button_states()


    # Handle Encyclopedia Buttons - opens encyclopedia view
    def create_encyclopedia_button(self, button_type, row=1):
        labels = {
            "user_encyclopedia": "User Encyclopedia",
            "server_encyclopedia": "Server Encyclopedia",
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
    def create_help_button(self):
        button = discord.ui.Button(
            label="help",
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

                help_text = (
                    "**TGOMMO Menu Help**\n\n"
                    "• **User Encyclopedia**: View your personal encyclopedia of caught creatures.\n"
                    "• **Server Encyclopedia**: View the server-wide encyclopedia of all creatures caught by members.\n"
                    "• **Close**: Close this menu.\n\n"
                    "Use the buttons above to navigate through the options. Only you can interact with this menu."
                )

                await interaction.followup.send(help_text, ephemeral=True)

        return callback


    # Handle Close Button
    def create_close_button(self):
        button = discord.ui.Button(
            label="close",
            style=discord.ButtonStyle.red,
            row=2  # Place in third row
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


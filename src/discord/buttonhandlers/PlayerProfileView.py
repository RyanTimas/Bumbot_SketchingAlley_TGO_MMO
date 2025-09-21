import asyncio
from webbrowser import open_new_tab

import discord
from src.commons.CommonFunctions import convert_to_png
from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.image_factories.PlayerProfilePageFactory import PlayerProfilePageFactory


class PlayerProfileView(discord.ui.View):
    def __init__(self, user_id, player_profile_image_factory: PlayerProfilePageFactory, tab_is_open=False, open_tab='Team'):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.player_profile_image_factory = player_profile_image_factory
        self.tab_is_open = tab_is_open
        self.open_tab = open_tab

        # Add a lock to prevent concurrent button interactions
        self.interaction_lock = asyncio.Lock()

        # Initialize the buttons once
        self.panel_toggle_button = self.create_panel_toggle_button()
        # self.prev_button = self.create_navigation_button(is_next=False)
        # self.next_button = self.create_navigation_button(is_next=True)
        self.close_button = self.create_close_button()

        # Add buttons to view
        self.add_item(self.panel_toggle_button)
        # self.add_item(self.prev_button)
        # self.add_item(self.next_button)
        self.add_item(self.close_button)

        # Update button states
        # self.update_button_states()


    def update_button_states(self):
        self.tab_is_open = not self.tab_is_open
        self.panel_toggle_button.label = "Close Panel" if self.tab_is_open else "Open Panel"
        self.panel_toggle_button.emoji = "➡️" if self.tab_is_open else "⬅️"


    # create buttons
    def create_panel_toggle_button(self):
        button = discord.ui.Button(
            label="Close Panel" if self.tab_is_open else "Open Panel",
            style=discord.ButtonStyle.primary,
            row=1,  # Place in second row
            emoji="➡️" if self.tab_is_open else "⬅️"
        )
        button.callback = self.panel_toggle_callback()
        return button

    def create_close_button(self):
        button = discord.ui.Button(
            label="✘",
            style=discord.ButtonStyle.red,
            row=2  # Place in third row
        )
        button.callback = self.close_callback()
        return button


    # handle button behavior
    def panel_toggle_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.user_id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                new_image = self.player_profile_image_factory.build_player_profile_page_image(tab_is_open=not self.tab_is_open)
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'player_profile_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def close_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.user_id):
                return

            # For delete operation, we need a shorter lock
            async with self.interaction_lock:
                # Delete the message
                await interaction.message.delete()

        return callback


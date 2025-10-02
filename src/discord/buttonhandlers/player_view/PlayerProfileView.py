import asyncio

import discord

from src.commons.CommonFunctions import convert_to_png, create_go_back_button
from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.buttonhandlers.player_view.UpdatePlayerProfileView import UpdatePlayerProfileView
from src.discord.image_factories.PlayerProfilePageFactory import PlayerProfilePageFactory


class PlayerProfileView(discord.ui.View):
    def __init__(self, user_id, player_profile_image_factory: PlayerProfilePageFactory, tab_is_open=False, open_tab='Team', original_view=None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.player_profile_image_factory = player_profile_image_factory
        self.tab_is_open = tab_is_open
        self.open_tab = open_tab
        self.original_view = original_view

        # Add a lock to prevent concurrent button interactions
        self.interaction_lock = asyncio.Lock()

        # Initialize the buttons once
        self.panel_toggle_button = self.create_panel_toggle_button()
        self.update_player_profile_button = self.update_player_profile_button(row=1)

        self.close_button = self.create_close_button()
        self.go_back_button = create_go_back_button(original_view=self.original_view, row=2, interaction_lock=self.interaction_lock, message_author_id=self.user_id)


        # Add buttons to view
        # row 1
        self.add_item(self.panel_toggle_button)
        # row 2
        self.add_item(self.update_player_profile_button)
        # row 3
        self.add_item(self.close_button)
        if self.original_view is not None:
            self.add_item(self.go_back_button)



    def update_button_states(self):
        self.tab_is_open = not self.tab_is_open
        self.panel_toggle_button.label = "Close Panel" if self.tab_is_open else "Open Panel"
        self.panel_toggle_button.emoji = "➡️" if self.tab_is_open else "⬅️"


    def create_panel_toggle_button(self):
        button = discord.ui.Button(
            label="Close Panel" if self.tab_is_open else "Open Panel",
            style=discord.ButtonStyle.primary,
            row=1,  # Place in second row
            emoji="➡️" if self.tab_is_open else "⬅️"
        )
        button.callback = self.panel_toggle_callback()
        return button
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


    def create_close_button(self):
        button = discord.ui.Button(
            label="✘",
            style=discord.ButtonStyle.red,
            row=2  # Place in third row
        )
        button.callback = self.close_callback()
        return button
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


    def update_player_profile_button(self, row = 2):
        button = discord.ui.Button(
            label="Update Player Profile",
            style=discord.ButtonStyle.green,
            row=row,  # Place in second row
        )
        button.callback = self.update_player_profile_callback()
        return button
    def update_player_profile_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.user_id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                player = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=self.user_id, convert_to_object=True)
                await interaction.followup.send("Are you sure you want to change your display creatures? *(Note: This changes YOUR display creatures)*", ephemeral=True, view=UpdatePlayerProfileView(interaction=interaction, user_id=self.user_id, player=player))
        return callback

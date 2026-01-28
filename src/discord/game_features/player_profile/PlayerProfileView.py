import asyncio

import discord

from src.commons.CommonFunctions import convert_to_png, create_go_back_button, create_close_button
from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.alert_center.AlertCenterView import AlertCenterView
from src.discord.game_features.player_profile.UpdatePlayerProfileView import UpdatePlayerProfileView
from src.discord.game_features.player_profile.PlayerProfilePageFactory import PlayerProfilePageFactory, TEAM, COLLECTIONS


class PlayerProfileView(discord.ui.View):
    def __init__(self, user, player_profile_image_factory: PlayerProfilePageFactory, tab_is_open=False, open_tab=TEAM, original_view=None, profile_user_id=None):
        super().__init__(timeout=None)
        self.user = user
        self.user_id = user.id
        self.profile_user_id = profile_user_id if profile_user_id is not None else self.user_id
        self.player = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=self.profile_user_id, convert_to_object=True)

        self.player_profile_image_factory = player_profile_image_factory
        self.tab_is_open = tab_is_open
        self.open_tab = open_tab
        self.original_view = original_view

        # Add a lock to prevent concurrent button interactions
        self.interaction_lock = asyncio.Lock()

        # Initialize the buttons once
        self.update_player_profile_button = self.update_player_profile_button(row=0)
        self.alert_center_button = self.create_alert_center_button(row=0)

        self.panel_toggle_button = self.create_panel_toggle_button()
        self.open_teams_panel_button = self.create_open_teams_panel_button()
        self.open_collections_panel_button = self.create_open_collections_panel_button()

        self.close_button = create_close_button(interaction_lock=self.interaction_lock, message_author_id=self.user_id, row=2)
        self.go_back_button = create_go_back_button(original_view=self.original_view, row=2, interaction_lock=self.interaction_lock, message_author_id=self.user_id)

        # Add buttons to view
        # row 1
        if self.user_id == self.profile_user_id:
            self.add_item(self.update_player_profile_button)
            self.add_item(self.alert_center_button)

        # row 2
        self.add_item(self.panel_toggle_button)
        if self.tab_is_open:
            self.add_item(self.open_teams_panel_button)
            self.add_item(self.open_collections_panel_button)

        # row 3
        self.add_item(self.close_button)
        if self.original_view is not None:
            self.add_item(self.go_back_button)


    def update_button_states(self, change_tab_open_property=False):
        self.tab_is_open = not self.tab_is_open if change_tab_open_property else self.tab_is_open
        self.panel_toggle_button.label = "Close Panel" if self.tab_is_open else "Open Panel"
        self.panel_toggle_button.emoji = "➡️" if self.tab_is_open else "⬅️"

        self.open_teams_panel_button.style = discord.ButtonStyle.green if self.open_tab == TEAM else discord.ButtonStyle.gray
        self.open_collections_panel_button.style = discord.ButtonStyle.green if self.open_tab == COLLECTIONS else discord.ButtonStyle.gray

        if change_tab_open_property:
            if self.tab_is_open:
                self.add_item(self.open_teams_panel_button)
                self.add_item(self.open_collections_panel_button)
            else:
                self.remove_item(self.open_teams_panel_button)
                self.remove_item(self.open_collections_panel_button)


    def create_panel_toggle_button(self, row=1):
        button = discord.ui.Button(
            label="Close Panel" if self.tab_is_open else "Open Panel",
            style=discord.ButtonStyle.primary,
            row=row,  # Place in second row
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
                self.update_button_states(change_tab_open_property=True)

                # Send updated view
                file = convert_to_png(new_image, f'player_profile_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def create_open_teams_panel_button(self, row=1):
        button = discord.ui.Button(
            label="See Team",
            style=discord.ButtonStyle.primary,
            row=row  # Place in second row
        )
        button.callback = self.open_teams_panel_callback()
        return button
    def open_teams_panel_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.user_id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                new_image = self.player_profile_image_factory.build_player_profile_page_image(tab_is_open=True, open_tab=TEAM)
                self.open_tab = TEAM
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'player_profile_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def create_open_collections_panel_button(self, row=1):
        button = discord.ui.Button(
            label="See Collections",
            style=discord.ButtonStyle.primary,
            row=row  # Place in second row
        )
        button.callback = self.open_collections_panel_callback()
        return button
    def open_collections_panel_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.user_id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                new_image = self.player_profile_image_factory.build_player_profile_page_image(tab_is_open=True, open_tab=COLLECTIONS)
                self.open_tab = COLLECTIONS
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'player_profile_page.png')
                await interaction.message.edit(attachments=[file], view=self)

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
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.profile_user_id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()
                await interaction.followup.send(f"{self.user.mention} Welcome to the Player Profile Editor!*", ephemeral=False, view=UpdatePlayerProfileView(interaction=interaction, user_id=self.user_id, player=self.player, player_profile_image_factory=self.player_profile_image_factory, original_view=self, original_message=interaction.message))
        return callback

    def create_alert_center_button(self, row=0):
        button = discord.ui.Button(
            label="Alert Center",
            style=discord.ButtonStyle.red,
            row=row,
            emoji="🔔"
        )
        button.callback = self.alert_center_callback()
        return button
    def alert_center_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.user_id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                alert_center_view = AlertCenterView(target_user=self.user, original_view=self)
                await interaction.followup.send(f"{self.user.mention} Welcome to the Alert Center!", ephemeral=False, view=alert_center_view)
        return callback

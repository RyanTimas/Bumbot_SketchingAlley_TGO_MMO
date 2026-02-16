import discord

from src.commons.CommonFunctions import convert_to_png, interaction_guard
from src.commons.CommonFunctions import retry_on_ssl_error
from src.discord.game_features.alert_center.AlertCenterView import AlertCenterView
from src.discord.game_features.player_profile.UpdatePlayerProfileView import UpdatePlayerProfileView
from src.discord.game_features.player_profile.PlayerProfileImageFactory import PlayerProfileImageFactory, \
    PLAYER_PROFILE_TAB_OPEN_TEAM, PLAYER_PROFILE_TAB_OPEN_COLLECTIONS, PLAYER_PROFILE_TAB_CLOSED
from src.discord.general.template.BaseView import BaseView


class PlayerProfileView(BaseView):
    def __init__(self, message_author, target_user, player_profile_image_factory: PlayerProfileImageFactory, original_view=None, tab_is_open=False, open_tab=PLAYER_PROFILE_TAB_OPEN_TEAM):
        super().__init__(message_author=message_author, target_user=target_user, image_factory=player_profile_image_factory, original_view=original_view)
        self.tab_is_open = tab_is_open
        self.open_tab = open_tab

        # DECLARE VIEW ITEMS
        self.update_player_profile_button = self.update_player_profile_button(row=0)
        self.alert_center_button = self.create_alert_center_button(row=0)

        self.panel_toggle_button = self.create_panel_toggle_button(row=1)
        self.open_teams_panel_button = self.create_open_teams_panel_button(row=1)
        self.open_collections_panel_button = self.create_open_collections_panel_button(row=1)

        # Add buttons to view
        super().refresh_view()

    def create_panel_toggle_button(self, row=1):
        button = discord.ui.Button(label="Close Panel" if self.tab_is_open else "Open Panel", style=discord.ButtonStyle.primary, row=row, emoji="➡️" if self.tab_is_open else "⬅️")
        button.callback = self.panel_toggle_callback()
        return button
    def panel_toggle_callback(self):
        @retry_on_ssl_error()
        async def callback(interaction):
            await interaction.response.defer()

            self.tab_is_open = not self.tab_is_open
            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def create_open_teams_panel_button(self, row=1):
        button = discord.ui.Button(label="See Team", style=discord.ButtonStyle.primary, row=row)
        button.callback = self.open_teams_panel_callback()
        return button
    def open_teams_panel_callback(self):
        @retry_on_ssl_error()
        async def callback(interaction):
            await interaction.response.defer()

            self.open_tab = PLAYER_PROFILE_TAB_OPEN_TEAM
            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def create_open_collections_panel_button(self, row=1):
        button = discord.ui.Button(label="See Collections", style=discord.ButtonStyle.primary, row=row)
        button.callback = self.open_collections_panel_callback()
        return button
    def open_collections_panel_callback(self):
        @retry_on_ssl_error()
        async def callback(interaction):
            await interaction.response.defer()

            self.open_tab = PLAYER_PROFILE_TAB_OPEN_COLLECTIONS
            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def update_player_profile_button(self, row = 2):
        button = discord.ui.Button(label="Update Player Profile", style=discord.ButtonStyle.green, row=row,)
        button.callback = self.update_player_profile_callback()
        return button
    def update_player_profile_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            update_player_profile_view = UpdatePlayerProfileView(message_author=self.message_author, player_profile_image_factory=self.image_factory, interaction=interaction, original_view=self, original_message=interaction.message)
            await interaction.followup.send(f"{self.target_user.discord_profile.mention} Welcome to the Player Profile Editor!*", view=update_player_profile_view, ephemeral=False)
        return callback

    def create_alert_center_button(self, row=0):
        button = discord.ui.Button(label="Alert Center", style=discord.ButtonStyle.red, row=row, emoji="🔔")
        button.callback = self.alert_center_callback()
        return button
    def alert_center_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            alert_center_view = AlertCenterView(target_user=self.target_user)
            await interaction.followup.send(f"{self.target_user.discord_profile.mention} Welcome to the Alert Center!", ephemeral=False, view=alert_center_view)
        return callback


    # SUPPORT FUNCTIONS
    def update_view_items(self):
        self.panel_toggle_button.label = "Close Panel" if self.tab_is_open else "Open Panel"
        self.panel_toggle_button.emoji = "➡️" if self.tab_is_open else "⬅️"

        self.open_teams_panel_button.style = discord.ButtonStyle.green if self.open_tab == PLAYER_PROFILE_TAB_OPEN_TEAM else discord.ButtonStyle.gray
        self.open_collections_panel_button.style = discord.ButtonStyle.green if self.open_tab == PLAYER_PROFILE_TAB_OPEN_COLLECTIONS else discord.ButtonStyle.gray

        if self.tab_is_open:
            if self.tab_is_open:
                self.add_item(self.open_teams_panel_button)
                self.add_item(self.open_collections_panel_button)
            else:
                self.remove_item(self.open_teams_panel_button)
                self.remove_item(self.open_collections_panel_button)
    def rebuild_view(self):
        super().rebuild_view()

        # Add buttons to view
        # row 1
        if self.message_author.user_id == self.target_user.user_id:
            self.add_item(self.update_player_profile_button)
            self.add_item(self.alert_center_button)

        # row 2
        self.add_item(self.panel_toggle_button)
        if self.tab_is_open:
            self.add_item(self.open_teams_panel_button)
            self.add_item(self.open_collections_panel_button)

    def reload_image(self):
        new_image = self.image_factory.reload_image(open_tab=self.open_tab if self.tab_is_open else PLAYER_PROFILE_TAB_CLOSED)
        return convert_to_png(new_image, 'player_profile_image.png')


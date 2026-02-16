import asyncio

import discord

from src.commons.CommonFunctions import interaction_guard
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.general_constants import TGOMMO_ROLE_ID


class AlertCenterView(BaseView):
    def __init__(self, target_user):
        super().__init__(message_author=target_user, target_user=target_user)
        self.megaphone_button = self.create_role_toggle_button(row=0)
        self.refresh_view()

    def create_role_toggle_button(self, row=0):
        has_role = discord.utils.get(self.target_user.discord_profile.roles, id=TGOMMO_ROLE_ID) is not None
        button_text = "Turn off Megaphone" if has_role else "Turn on Megaphone"
        button_style = discord.ButtonStyle.green if has_role else discord.ButtonStyle.gray

        button = discord.ui.Button(label=button_text, style=button_style, emoji="📢", row=row)
        button.callback = self.role_toggle_callback()
        return button
    def role_toggle_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            tgommo_role = interaction.guild.get_role(TGOMMO_ROLE_ID)
            if not tgommo_role:
                await interaction.response.send_message("TGOMMO role not found in this server.", ephemeral=True)
                return

            # Handle role assignment/removal
            has_role = tgommo_role in self.target_user.discord_profile.roles
            await self.target_user.discord_profile.remove_roles(tgommo_role) if has_role else await self.target_user.discord_profile.add_roles(tgommo_role)
            await interaction.response.send_message(f"Megaphone is now {'off' if has_role else 'on'}. You will {"no longer" if has_role else "now"} be notified when a creature spawns.", ephemeral=True)

            self.refresh_view()
            await  interaction.message.edit(view=self)
        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def update_button_states(self):
        self.megaphone_button.style = discord.ButtonStyle.green if discord.utils.get(self.target_user.discord_profile.roles, id=TGOMMO_ROLE_ID) is not None else discord.ButtonStyle.gray
        self.megaphone_button.label = "Turn off Megaphone" if discord.utils.get(self.target_user.discord_profile.roles, id=TGOMMO_ROLE_ID) is not None else "Turn on Megaphone"
    def rebuild_view(self):
        super().rebuild_view()

        self.add_item(self.megaphone_button)

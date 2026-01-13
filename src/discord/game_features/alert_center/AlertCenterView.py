import asyncio

import discord

from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view, convert_to_png, \
    create_go_back_button, create_close_button
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous
from src.discord.game_features.avatar_board.AvatarBoardImageFactory import AvatarBoardImageFactory, AVATAR_QUESTS, \
    UNLOCKED_AVATARS
from src.resources.constants.general_constants import TGOMMO_ROLE_ID


class AlertCenterView(discord.ui.View):
    def __init__(self, target_user, original_view=None):
        super().__init__(timeout=None)
        self.target_user = target_user

        self.interaction_lock = asyncio.Lock()
        self.original_view = original_view

        self.megaphone_button = self.create_role_toggle_button(row=0)
        self.close_button = create_close_button(interaction_lock=self.interaction_lock, message_author_id=self.target_user.id, row=3)
        self.refresh_view()

    def create_role_toggle_button(self, row=0):
        # Check if user currently has the role to determine button text
        has_role = discord.utils.get(self.target_user.roles, id=TGOMMO_ROLE_ID) is not None
        button_text = "Turn off Megaphone" if has_role else "Turn on Megaphone"
        button_style = discord.ButtonStyle.green if has_role else discord.ButtonStyle.gray

        button = discord.ui.Button(
            label=button_text,
            style=button_style,
            emoji="📢",
            row=row
        )
        button.callback = self.role_toggle_callback()
        return button

    def role_toggle_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, None if not self.target_user else self.target_user.id):
                return

            tgommo_role = interaction.guild.get_role(TGOMMO_ROLE_ID)
            if not tgommo_role:
                await interaction.response.send_message("TGOMMO role not found in this server.", ephemeral=True)
                return

            # Handle role assignment/removal
            has_role = tgommo_role in self.target_user.roles
            await self.target_user.remove_roles(tgommo_role) if has_role else await self.target_user.add_roles(tgommo_role)
            await interaction.response.send_message(f"Megaphone is now {'off' if has_role else 'on'}. You will {"no longer" if has_role else "now"} be notified when a creature spawns.", ephemeral=True)

            # Update the button to reflect the new state
            self.refresh_view()
            await  interaction.message.edit(view=self)

        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        self.megaphone_button.style = discord.ButtonStyle.green if discord.utils.get(self.target_user.roles, id=TGOMMO_ROLE_ID) is not None else discord.ButtonStyle.gray
        self.megaphone_button.label = "Turn off Megaphone" if discord.utils.get(self.target_user.roles, id=TGOMMO_ROLE_ID) is not None else "Turn on Megaphone"
    def rebuild_view(self):
        self.clear_items()

        self.add_item(self.megaphone_button)
        self.add_item(self.close_button)
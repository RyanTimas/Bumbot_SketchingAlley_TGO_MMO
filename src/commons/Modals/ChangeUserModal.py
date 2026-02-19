import discord

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler


class ChangeUserModal(discord.ui.Modal):
    def __init__(self, view, server_access=False):
        super().__init__(title="Change Target Player")
        self.view = view
        self.server_access = server_access
        self.user_id_input = discord.ui.TextInput(label="User ID", placeholder=f"Enter user ID... {"(Leave blank for server view)" if server_access else "(Leave blank for self)"}", required=False, max_length=20)
        self.add_item(self.user_id_input)

    async def on_submit(self, interaction):
        try:
            user_id = self.user_id_input.value
            if self.user_id_input.value.strip() == "":
                user_id = 0 if self.server_access else interaction.user.id
            new_target_user = get_tgommo_db_handler().get_user_profile_by_user_id(int(user_id))

            self.view.target_user = new_target_user
            reloaded_image = self.view.reload_image(target_user=new_target_user)
            self.view.refresh_view()
            await interaction.response.edit_message(attachments=[reloaded_image], view=self.view)
        except ValueError:
            await interaction.response.send_message("Invalid user ID format!", ephemeral=True)
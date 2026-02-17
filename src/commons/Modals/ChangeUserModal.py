import discord

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler


class ChangeUserModal(discord.ui.Modal):
    def __init__(self, view):
        super().__init__(title="Change Target Player")
        self.view = view
        self.user_id_input = discord.ui.TextInput(
            label="User ID",
            placeholder="Enter user ID... (Leave blank for server view)",
            required=False,
            max_length=20
        )
        self.add_item(self.user_id_input)

    async def on_submit(self, interaction):
        try:
            user_id = self.user_id_input.value.strip()
            reloaded_image = self.view.reload_image(target_user=get_tgommo_db_handler().get_user_profile_by_user_id(0 if user_id == "" else int(self.user_id_input.value)))
            self.view.refresh_view()
            await interaction.response.edit_message(attachments=[reloaded_image], view=self.view)
        except ValueError:
            await interaction.response.send_message("Invalid user ID format!", ephemeral=True)
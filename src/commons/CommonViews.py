import discord
from typing import Any, cast

class ConfirmationView(discord.ui.View):
    def __init__(self, original_view=None, original_message=None, on_confirm=None, on_cancel=None):
        super().__init__()
        self.original_view = original_view
        self.original_message = original_message
        self._on_confirm = on_confirm if on_confirm is not None else default_confirm
        self._on_cancel = on_cancel if on_cancel is not None else default_cancel

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # defer immediately to meet 3s rule
        await cast(Any, interaction.response).defer()
        await self._on_confirm(interaction)

        # disable buttons and update the ephemeral message
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await cast(Any, interaction.response).defer()
        await self._on_cancel(interaction)

        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)
        await interaction.followup.send("Cancelled.", ephemeral=True)

# Reusable ephemeral confirmation child view - has yes or no buttons and calls the provided callbacks when pressed
async def default_confirm(interaction: discord.Interaction):
    await interaction.followup.send("Confirmed.", ephemeral=True)
async def default_cancel(interaction: discord.Interaction):
    await interaction.followup.send("Cancelled.", ephemeral=True)
import discord
from discord.ui import Button, Modal, TextInput

from src.commons.CommonFunctions import retry_on_ssl_error
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord import DiscordBot
from src.discord.handlers import CreatureNicknameHandler


class NicknameModal(Modal):
    def __init__(self, creature_id):
        super().__init__(title="Set Creature Nickname")
        self.creature_id = creature_id

        self.nickname_input = TextInput(
            label="Nickname",
            placeholder="Enter a nickname for your creature",
            max_length=50,
            required=True
        )

        self.add_item(self.nickname_input)

    async def on_submit(self, interaction: discord.Interaction):
        nickname = self.nickname_input.value
        get_tgommo_db_handler().update_creature_nickname(self.creature_id, nickname)

        await interaction.response.send_message(f"Nickname set to: {nickname}", ephemeral=True)


class CreatureNicknameView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, creature_id: int):
        super().__init__(timeout=None)

        self.creature_id = creature_id
        self.interaction = interaction

        # Add nickname button
        self.add_item(self.create_nickname_button())

    def create_nickname_button(self):
        button = Button(label="Set Nickname", style=discord.ButtonStyle.red)
        button.callback = self.nickname_button_callback
        return button

    async def nickname_button_callback(self, interaction: discord.Interaction):
        modal = NicknameModal(self.creature_id)
        await interaction.response.send_modal(modal)

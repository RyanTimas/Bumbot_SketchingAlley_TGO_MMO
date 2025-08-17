import discord
from discord import Message
from discord.ui import View

from src.database.handlers import DatabaseHandler


class CatchButton(discord.ui.Button):
    def __init__(self, discord_bot, message: Message, database_handler: DatabaseHandler):
        super().__init__(label="Catch Critter!!", style=discord.ButtonStyle.blurple)
        self.discord_bot = discord_bot
        self.message = message
        self.database_handler = database_handler


    async def callback(self, interaction: discord.Interaction):
        success_message = await interaction.channel.send("Success!!")
        self.database_handler.user_database_handler.update_xp(10000, interaction.user.id, interaction.user.display_name)

        await interaction.message.delete()
        await success_message.delete(delay=5)


class TGOMMOCatchButtonView(View):
    def __init__(self, discord_bot, message, database_handler):
        super().__init__(timeout=None)
        self.add_item(CatchButton(discord_bot=discord_bot, message=message, database_handler=database_handler))
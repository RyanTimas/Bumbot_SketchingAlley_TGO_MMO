import discord
from discord import Message
from discord.ui import View

from src.database.handlers import DatabaseHandler
from src.discord.embeds.CreatureEmbedHandler import CreatureEmbedHandler
from src.discord.objects.TGOCreature import TGOCreature


class CatchButton(discord.ui.Button):
    def __init__(self, discord_bot, message: Message, database_handler: DatabaseHandler, creature:TGOCreature):
        super().__init__(label="Catch Critter!!", style=discord.ButtonStyle.blurple)
        self.discord_bot = discord_bot
        self.message = message
        self.database_handler = database_handler
        self.creature = creature


    async def callback(self, interaction: discord.Interaction):

        successful_catch_embed = CreatureEmbedHandler(self.creature).generate_catch_embed(interaction.user)

        success_message = await interaction.channel.send(embed=successful_catch_embed[0], files=[successful_catch_embed[1]])
        #self.database_handler.user_database_handler.update_xp(10000, interaction.user.id, interaction.user.display_name)

        # todo: check database to see if user already has this creature
        # todo: check to see if creature has already been caught on the server
        await interaction.response.send_message(f"Success!! you've successfully caught {self.creature.name}", ephemeral=True)

        await interaction.message.delete()
        # await success_message.delete(delay=5)


class TGOMMOCatchButtonView(View):
    def __init__(self, discord_bot, message, database_handler, creature:TGOCreature):
        super().__init__(timeout=None)
        self.add_item(CatchButton(discord_bot=discord_bot, message=message, database_handler=database_handler, creature=creature))
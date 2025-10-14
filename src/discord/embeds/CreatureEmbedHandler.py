import datetime
import time
from random import randint

import discord
from PIL import Image

from src.commons.CommonFunctions import build_image_file, to_grayscale, convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.handlers.EncounterImageHandler import EncounterImageHandler
from src.discord.objects import TGOCreature
from src.discord.objects.CreatureRarity import MYTHICAL
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import TGOMMO_CREATURE_EMBED_GRASS_ICON, IMAGE_FOLDER_CREATURES_PATH, \
    ENCOUNTER_SCREEN_THUMBNAIL_SUFFIX


class CreatureEmbedHandler:
    def __init__(self, creature:TGOCreature, environment:TGOEnvironment=None, time_of_day=None):
        self.creature = creature
        self.environment = environment
        self.time_of_day = time_of_day
        self.catch_user = None
        self.interaction = None


    def generate_spawn_embed(self):
        thumbnail_img = Image.open(f"{IMAGE_FOLDER_CREATURES_PATH}\\{self.creature.img_root}{ENCOUNTER_SCREEN_THUMBNAIL_SUFFIX}")
        thumbnail_img = convert_to_png(image=thumbnail_img, file_name="thumbnail.png")

        encounter_img_handler = EncounterImageHandler(creature=self.creature, environment=self.environment, time_of_day=self.time_of_day)
        encounter_img = encounter_img_handler.create_encounter_image()

        embed = discord.Embed(color=self.creature.rarity.color)
        embed.set_author(name = f'A wild {self.creature.name} appears!!', icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),

        embed.add_field(name="Rarity", value=f"{self.creature.rarity.emojii} **{self.creature.rarity.name}**",inline=True)
        embed.add_field(name="Despawn Timer", value=f"🕒 *Despawns {self.get_despawn_timestamp()}*", inline=True)

        if self.time_of_day:
            embed.set_footer(text=f'{'🌙 Night' if self.environment.is_night_environment else '☀️ Day'}')

        embed.timestamp = discord.utils.utcnow()
        embed.set_image(url=f"attachment://{encounter_img.filename}")

        embed.set_thumbnail(url=f"attachment://thumbnail.png")
        return embed, thumbnail_img, encounter_img

    def generate_despawn_embed(self):
        thumbnail_img = Image.open(f"{IMAGE_FOLDER_CREATURES_PATH}\\{self.creature.img_root}{ENCOUNTER_SCREEN_THUMBNAIL_SUFFIX}")
        thumbnail_img = convert_to_png(image=thumbnail_img, file_name="thumbnail.png")

        encounter_img_handler = EncounterImageHandler(creature=self.creature, environment=self.environment, time_of_day=self.time_of_day)
        encounter_img = encounter_img_handler.create_encounter_image()

        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name = f"The {self.creature.name} has run away...", icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),

        embed.add_field(name=f"Despawned - {self.get_despawn_timestamp(is_countdown=False)}", value=f'', inline=True)
        thumbnail_img = to_grayscale(thumbnail_img)
        thumbnail_img.filename = "thumbnail.png"

        embed.set_thumbnail(url=f"attachment://thumbnail.png")
        return embed, thumbnail_img, encounter_img


    def generate_catch_embed(self, interaction: discord.Interaction= None, nickname: str = None):
        if interaction:
            self.interaction = interaction
            self.catch_user = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=interaction.user.id, convert_to_object=True)

        thumbnail_img = Image.open(f"{IMAGE_FOLDER_CREATURES_PATH}\\{self.creature.img_root}{ENCOUNTER_SCREEN_THUMBNAIL_SUFFIX}")
        embed = discord.Embed(color=discord.Color.dark_green())

        embed.set_author(name = f'The {self.creature.name.upper()} was caught!', icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),
        embed.add_field(name=f"✨     Caught By - **{self.catch_user.nickname}** *({self.interaction.user.name.upper()})*", value=f"", inline=False)
        if nickname:
            embed.add_field(name=f"‼️     Nickname - **{nickname}**", value=f"", inline=False)
        embed.add_field(name=f"🕒     Caught On - **{discord.utils.utcnow().strftime('%Y-%m-%d %H:%M UTC')}**\n\n\n\n", value=f"", inline=False)

        embed.add_field(name=CREATURE_DIVIDER_LINE, value=f"", inline=False)

        # calculate xp to add and add fields to embed
        total_xp, embed = self.calculate_catch_xp(catch_embed=embed, interaction=self.interaction)

        embed.add_field(name=CREATURE_DIVIDER_LINE, value=f"", inline=False)
        embed.add_field(name=f"✨ **Total {total_xp} xp** ✨", value=f"", inline=False)

        thumbnail_png = convert_to_png(image=thumbnail_img, file_name="thumbnail.png")
        embed.set_thumbnail(url=f"attachment://thumbnail.png")
        embed.timestamp = discord.utils.utcnow()

        return embed, thumbnail_png, total_xp


    def get_despawn_timestamp(self, is_countdown: bool = True):
        despawn_timestamp = self.creature.spawn_time + self.creature.despawn_time
        despawn_character = 'R' if is_countdown else 'F'
        return f"<t:{despawn_timestamp}:{despawn_character}>"


    def calculate_catch_xp(self, catch_embed: discord.Embed, interaction: discord.Interaction):
        total_xp = randint(10, 50)

        total_user_catches = get_tgommo_db_handler().get_total_user_catches_for_species(user_id=interaction.user.id, dex_no=self.creature.dex_no, variant_no=self.creature.variant_no)
        total_server_catches = get_tgommo_db_handler().get_total_server_catches_for_species(creature_id=self.creature.creature_id)

        catch_embed.add_field(name=CREATURE_SUCCESSFUL_CATCH_LINE + f'*+{total_xp} xp*', value=f"", inline=False)

        if 0 == total_user_catches:
            catch_embed.add_field(name=CREATURE_FIRST_CATCH_LINE, value=f"", inline=False)
            total_xp += 2500
        if 0 == total_server_catches:
            catch_embed.add_field(name=CREATURE_FIRST_SERVER_CATCH_LINE, value=f"", inline=False)
            total_xp += 10000
        if self.creature.rarity == MYTHICAL:
            catch_embed.add_field(name=MYTHICAL_CATCH_LINE, value=f"", inline=False)
            total_xp += 10000

        return total_xp, catch_embed
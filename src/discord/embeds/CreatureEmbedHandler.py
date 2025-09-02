import io
import random
import time
from pickle import FALSE
from random import randint

import discord
from discord import File

from src.commons.CommonFunctions import build_image_file, to_grayscale, get_image_path
from src.database.handlers import DatabaseHandler
from src.database.handlers.DatabaseHandler import get_db_handler, get_tgommo_db_handler
from src.discord.handlers.EncounterImageHandler import EncounterImageHandler
from src.discord.objects import TGOCreature
from src.discord.objects.CreatureRarity import MYTHICAL
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import TGOMMO_CREATURE_EMBED_GRASS_ICON


class CreatureEmbedHandler:
    def __init__(self, creature:TGOCreature, environment:TGOEnvironment=None):
        self.creature = creature
        self.environment = environment

    def generate_spawn_embed(self, is_spawn_message: bool = True):
        thumbnail_img = build_image_file(self.creature.img_root + '_THUMB')
        environment_img = build_image_file(self.environment.img_root)

        encounter_img_handler = EncounterImageHandler(background_img_path=get_image_path(environment_img.filename), foreground_img_path=get_image_path(thumbnail_img.filename), creature=self.creature)
        encounter_img = encounter_img_handler.create_encounter_image()


        embed = discord.Embed(
            #title= f"✨A wild ***{self.creature.name.upper()}*** appears!!✨" if is_spawn_message else f"the wild ***{self.creature.name.upper()}*** has run away...",
            #description=f"This is a test description for the creature embed.",
            color=self.creature.rarity.color if is_spawn_message else discord.Color.dark_red()
        )
        embed.set_author(name = f'A wild {self.creature.name} appears!!' if is_spawn_message else f"The {self.creature.name} has run away...", icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),

        if is_spawn_message:
            embed.add_field(name="Rarity", value=f"{self.creature.rarity.emojii} **{self.creature.rarity.name}**",inline=True)
            embed.add_field(name="Despawn Timer", value=f"🕒 *Despawns {self.get_despawn_timestamp()}*", inline=True)

            embed.set_footer(text=f'{self.environment.location} ({'🌙 Night' if self.environment.is_night_environment else '☀️ Day'})', icon_url=TGOMMO_CREATURE_EMBED_LOCATION_ICON)
            embed.timestamp = discord.utils.utcnow()
            embed.set_image(url=f"attachment://{encounter_img.filename}")
        else:
            embed.add_field(name=f"Despawned - {self.get_despawn_timestamp(is_countdown=False)}", value=f'', inline=True)
            thumbnail_img = to_grayscale(thumbnail_img)

        embed.set_thumbnail(url=f"attachment://{thumbnail_img.filename}")

        return embed, thumbnail_img, encounter_img

    def generate_catch_embed(self, interaction: discord.Interaction):
        thumbnail_img = build_image_file(self.creature.img_root + '_THUMB')
        photo_img = build_image_file(self.creature.img_root)

        embed = discord.Embed(
            #title= f"{user.name} caught the wild ***{self.creature.name.upper()}***!",
            #description=f"This is a test description for the creature embed.",
            color=discord.Color.dark_green()
        )
        embed.set_author(name = f'The {self.creature.name.upper()} was caught!', icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),
        embed.add_field(name=f"✨     Caught By - **{interaction.user.name.upper()}**", value=f"", inline=False)
        embed.add_field(name=f"🕒     Caught On - **{discord.utils.utcnow().strftime('%Y-%m-%d %H:%M UTC')}**\n\n\n\n", value=f"", inline=False)

        embed.add_field(name=CREATURE_DIVIDER_LINE, value=f"", inline=False)

        # calculate xp to add and add fields to embed
        total_xp, embed = self.calculate_catch_xp(catch_embed=embed, interaction=interaction)

        embed.add_field(name=CREATURE_DIVIDER_LINE, value=f"", inline=False)
        embed.add_field(name=f"✨ **Total {total_xp} xp** ✨", value=f"", inline=False)

        # embed.set_image(url=f"attachment://{photo_img.filename}")
        embed.set_thumbnail(url=f"attachment://{thumbnail_img.filename}")

        # embed.set_footer(text ='Location | Forest (☀️ Day)', icon_url= CREATURE_EMBED_LOCATION_ICON)
        # embed.timestamp = discord.utils.utcnow()

        return embed, thumbnail_img, photo_img, total_xp


    def get_despawn_timestamp(self, is_countdown: bool = True):
        despawn_timestamp = int(time.time()) + self.creature.despawn_time * 60
        despawn_character = 'R' if is_countdown else 'F'

        return f"<t:{despawn_timestamp}:{despawn_character}>"


    def calculate_catch_xp(self, catch_embed: discord.Embed, interaction: discord.Interaction):
        total_xp = randint(100, 350)

        catch_embed.add_field(name=CREATURE_SUCCESSFUL_CATCH_LINE + f'*+{total_xp} xp*', value=f"", inline=False)

        if 0 == get_tgommo_db_handler().get_total_user_catches_for_species(user_id=interaction.user.id, dex_no=self.creature.dex_no, variant_no=self.creature.variant_no):
            catch_embed.add_field(name=CREATURE_FIRST_CATCH_LINE, value=f"", inline=False)
            total_xp += 2500

        if 0 == get_tgommo_db_handler().get_total_server_catches_for_species(creature_id=self.creature.creature_id):
            catch_embed.add_field(name=CREATURE_FIRST_SERVER_CATCH_LINE, value=f"", inline=False)
            total_xp += 10000

        if self.creature.rarity == MYTHICAL:
            catch_embed.add_field(name=MYTHICAL_CATCH_LINE, value=f"", inline=False)
            total_xp += 10000


        return total_xp, catch_embed
import random
import time
from pickle import FALSE

import discord

from src.commons.CommonFunctions import build_image_file, to_grayscale
from src.discord.handlers.EncounterImageHandler import EncounterImageHandler
from src.discord.objects import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import TGOMMO_CREATURE_EMBED_GRASS_ICON, TGOMMO_CREATURE_EMBED_LOCATION_ICON, \
    CREATURE_DIVIDER_LINE, CREATURE_SUCCESSFUL_CATCH_LINE, CREATURE_FIRST_CATCH_LINE, CREATURE_FIRST_SERVER_CATCH_LINE, \
    CREATURE_TOTAL_XP_LINE


class CreatureEmbedHandler:
    def __init__(self, creature:TGOCreature, environment:TGOEnvironment=None):
        self.creature = creature
        self.environment = environment

    def generate_spawn_embed(self, is_spawn_message: bool = True):
        thumbnail_img = build_image_file(self.creature.img_root + '_THUMB')
        photo_img = build_image_file(self.creature.img_root)

        embed = discord.Embed(
            #title= f"✨A wild ***{self.creature.name.upper()}*** appears!!✨" if is_spawn_message else f"the wild ***{self.creature.name.upper()}*** has run away...",
            #description=f"This is a test description for the creature embed.",
            color=self.creature.rarity.color if is_spawn_message else discord.Color.dark_red()
        )
        embed.set_author(name = f'A wild {self.creature.name} appears!!' if is_spawn_message else f"The {self.creature.name} has run away...", icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),

        if is_spawn_message:
            embed.add_field(name="Rarity", value=f"{self.creature.rarity.emojii} **{self.creature.rarity.name}**",inline=True)
            embed.add_field(name="Despawn Timer", value=f"🕒 *Despawns {self.get_despawn_timestamp()}*", inline=True)

            embed.set_footer(text='Location | Forest (☀️ Day)', icon_url=TGOMMO_CREATURE_EMBED_LOCATION_ICON)
            embed.timestamp = discord.utils.utcnow()
            embed.set_image(url=f"attachment://{photo_img.filename}")
        else:
            embed.add_field(name=f"Despawned - {self.get_despawn_timestamp(is_countdown=False)}", value=f'', inline=True)
            thumbnail_img = to_grayscale(thumbnail_img)

        embed.set_thumbnail(url=f"attachment://{thumbnail_img.filename}")

        return embed, thumbnail_img, photo_img

    def generate_catch_embed(self, user: discord.User):
        thumbnail_img = build_image_file(self.creature.img_root + '_THUMB')
        photo_img = build_image_file(self.creature.img_root)

        embed = discord.Embed(
            #title= f"{user.name} caught the wild ***{self.creature.name.upper()}***!",
            #description=f"This is a test description for the creature embed.",
            color=discord.Color.dark_green()
        )
        embed.set_author(name = f'The {self.creature.name.upper()} was caught!', icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),
        embed.add_field(name=f"✨     Caught By - **{user.name.upper()}**", value=f"", inline=False)
        embed.add_field(name=f"🕒     Caught On - **{discord.utils.utcnow().strftime('%Y-%m-%d %H:%M UTC')}**\n\n\n\n", value=f"", inline=False)

        embed.add_field(name=CREATURE_DIVIDER_LINE, value=f"", inline=False)
        embed.add_field(name=CREATURE_SUCCESSFUL_CATCH_LINE, value=f"", inline=False)
        embed.add_field(name=CREATURE_FIRST_CATCH_LINE, value=f"", inline=False)
        embed.add_field(name=CREATURE_FIRST_SERVER_CATCH_LINE, value=f"", inline=False)
        embed.add_field(name=CREATURE_DIVIDER_LINE, value=f"", inline=False)
        embed.add_field(name=CREATURE_TOTAL_XP_LINE, value=f"", inline=False)

        # embed.set_image(url=f"attachment://{photo_img.filename}")
        embed.set_thumbnail(url=f"attachment://{thumbnail_img.filename}")

        # embed.set_footer(text ='Location | Forest (☀️ Day)', icon_url= CREATURE_EMBED_LOCATION_ICON)
        # embed.timestamp = discord.utils.utcnow()

        return embed, thumbnail_img, photo_img


    def get_despawn_timestamp(self, is_countdown: bool = True):
        despawn_timestamp = int(time.time()) + self.creature.despawn_time * 60
        despawn_character = 'R' if is_countdown else 'F'

        return f"<t:{despawn_timestamp}:{despawn_character}>"
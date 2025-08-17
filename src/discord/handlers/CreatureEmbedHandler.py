import random
import time

import discord

from src.commons.CommonFunctions import build_image_file
from src.discord.objects import TGOCreature


class CreatureEmbedHandler:
    def __init__(self, creature:TGOCreature):
        self.creature = creature

    async def generate_spawn_embed(self, is_spawn_message: bool = True):
        thumbnail_img = build_image_file(self.creature.thumbnail_path)
        photo_img = build_image_file(self.creature.img_path)

        embed = discord.Embed(
            title= f"✨A wild ***{self.creature.name.upper()}*** appears!!✨" if is_spawn_message else f"the wild ***{self.creature.name.upper()}*** has run away...",
            #description=f"This is a test description for the creature embed.",
            color=discord.Color.purple()
        )

        embed.add_field(name="Rarity", value=f"🟪 **{self.creature.rarity}**", inline=True)
        embed.add_field(name="Despawn Timer", value=f"🕒 *Despawns {self.get_despawn_timestamp()}*", inline=True)

        embed.add_field(name="", value=f"", inline=True)

        embed.set_image(url=f"attachment://{photo_img.filename}")
        embed.set_thumbnail(url=f"attachment://{thumbnail_img.filename}")
        return embed, thumbnail_img, photo_img


    def get_despawn_timestamp(self):
        despawn_timestamp = int(time.time()) + self.creature.despawn_time * 60
        return f"<t:{despawn_timestamp}:R>"
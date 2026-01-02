from random import randint

import discord
from PIL import Image

from src.commons.CommonFunctions import to_grayscale, convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_enounter.EncounterImageHandler import EncounterImageHandler
from src.discord.objects import TGOCreature
from src.discord.objects.CreatureRarity import MYTHICAL, TRANSCENDANT
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import TGOMMO_CREATURE_EMBED_GRASS_ICON, IMAGE_FOLDER_CREATURES_PATH, \
    ENCOUNTER_SCREEN_THUMBNAIL_SUFFIX


class CreatureEmbedHandler:
    def __init__(self, creature:TGOCreature, environment:TGOEnvironment=None, spawn_user = None, time_of_day=None, active_bonuses = None):
        self.creature = creature
        self.environment = environment
        self.spawn_user = spawn_user
        self.active_bonuses = active_bonuses

        self.time_of_day = time_of_day
        self.catch_user = None
        self.interaction = None

        self.total_xp = 0
        self.xp_fields = []


    def generate_spawn_embed(self):
        thumbnail_img = convert_to_png(image=self.creature.creature_image, file_name="thumbnail.png")

        encounter_img_handler = EncounterImageHandler(creature=self.creature, environment=self.environment, time_of_day=self.time_of_day)
        encounter_img = encounter_img_handler.create_encounter_image()

        embed = discord.Embed(color=self.creature.local_rarity.color)

        creature_name = self.creature.name if self.creature.local_rarity.name != TRANSCENDANT.name else "❓❓❓"
        message = f'{self.spawn_user.nickname} has attracted a wild {creature_name}!' if self.spawn_user else f'A wild {creature_name} has appeared!'

        embed.set_author(name = message, icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),

        embed.add_field(name="Rarity", value=f"{self.creature.local_rarity.emojii} **{self.creature.local_rarity.name}**", inline=True)

        if self.creature.local_rarity.name != MYTHICAL.name and self.creature.local_rarity.name != TRANSCENDANT.name:
            embed.add_field(name="Despawn Timer", value=f"🕒 *Despawns {self.get_despawn_timestamp(timestamp=int(self.creature.despawn_time.timestamp()))}*", inline=True)

        # add active bonuses to embed
        bonus_description = ''
        for bonus in self.active_bonuses:
            bonus_description += f"-#\t{bonus.local_rarity.emojii} {bonus.bonus_name} - *Expires in {self.get_despawn_timestamp(timestamp=int(bonus.despawn_time.timestamp()))}*\n"
        if len(self.active_bonuses) > 0:
            embed.add_field(name=f"", value=f"", inline=False)
            embed.add_field(name=f"Active Bonuses", value=f"{bonus_description}", inline=False)


        if self.time_of_day:
            embed.set_footer(text=f'{'🌙 Night' if self.environment.is_night_environment else '☀️ Day'}')

        embed.timestamp = discord.utils.utcnow()
        embed.set_image(url=f"attachment://{encounter_img.filename}")

        embed.set_thumbnail(url=f"attachment://thumbnail.png")
        return embed, thumbnail_img, encounter_img

    def generate_despawn_embed(self):
        encounter_img_handler = EncounterImageHandler(creature=self.creature, environment=self.environment, time_of_day=self.time_of_day)
        encounter_img = encounter_img_handler.create_encounter_image()

        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name = f"The {self.creature.name} has run away...", icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),

        embed.add_field(name=f"Despawned - {self.get_despawn_timestamp(is_countdown=False, timestamp=int(self.creature.despawn_time.timestamp()))}", value=f'', inline=True)

        thumbnail_img = convert_to_png(image=self.creature.creature_image, file_name="thumbnail.png")
        thumbnail_img = to_grayscale(thumbnail_img)
        thumbnail_img.filename = "thumbnail.png"

        embed.set_thumbnail(url=f"attachment://thumbnail.png")
        return embed, thumbnail_img, encounter_img


    def generate_catch_embed(self, interaction: discord.Interaction= None, nickname: str = None):
        if interaction:
            self.interaction = interaction
            self.catch_user = get_tgommo_db_handler().get_user_profile_by_user_id(user_id=interaction.user.id, convert_to_object=True)

        embed = discord.Embed(color=discord.Color.dark_green())

        embed.set_author(name = f'The {self.creature.name.upper()} was caught!', icon_url= TGOMMO_CREATURE_EMBED_GRASS_ICON),
        embed.add_field(name=f"✨     Caught By - **{self.catch_user.nickname}** *({self.interaction.user.name.upper()})*", value=f"", inline=False)
        if nickname:
            embed.add_field(name=f"‼️     Nickname - **{nickname}**", value=f"", inline=False)
        embed.add_field(name=f"🕒     Caught On - **{discord.utils.utcnow().strftime('%Y-%m-%d %H:%M UTC')}**\n\n\n\n", value=f"", inline=False)

        embed.add_field(name=CREATURE_DIVIDER_LINE, value=f"", inline=False)

        # calculate xp to add and add fields to embed
        if self.total_xp == 0:
            self.total_xp, embed = self.calculate_catch_xp(catch_embed=embed, interaction=self.interaction)
        else:
            for field in self.xp_fields:
                embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])

        embed.add_field(name=CREATURE_DIVIDER_LINE, value=f"", inline=False)
        embed.add_field(name=f"✨ **Total {self.total_xp} xp** ✨", value=f"", inline=False)

        thumbnail_png = convert_to_png(image=self.creature.creature_image, file_name="thumbnail.png")
        embed.set_thumbnail(url=f"attachment://thumbnail.png")
        embed.timestamp = discord.utils.utcnow()

        return embed, thumbnail_png, self.total_xp


    def get_despawn_timestamp(self, is_countdown: bool = True, timestamp: int = None):
        despawn_character = 'R' if is_countdown else 'F'
        return f"<t:{timestamp}:{despawn_character}>"


    def calculate_catch_xp(self, catch_embed: discord.Embed, interaction: discord.Interaction):
        total_xp = randint(10, 50)

        user_has_caught_species = get_tgommo_db_handler().user_has_caught_species(user_id=interaction.user.id, creature_id=self.creature.catch_id)
        total_server_catches = get_tgommo_db_handler().get_total_server_catches_for_species(creature_id=self.creature.catch_id)

        self.add_xp_field_to_embed(name=CREATURE_SUCCESSFUL_CATCH_LINE + f'*+{total_xp} xp*', value=f"", inline=False)
        catch_embed.add_field(name=CREATURE_SUCCESSFUL_CATCH_LINE + f'*+{total_xp} xp*', value=f"", inline=False)

        if not user_has_caught_species:
            self.add_xp_field_to_embed(name=CREATURE_FIRST_CATCH_LINE, value=f"", inline=False)
            catch_embed.add_field(name=CREATURE_FIRST_CATCH_LINE, value=f"", inline=False)
            total_xp += 2500
        if 0 == total_server_catches:
            self.add_xp_field_to_embed(name=CREATURE_FIRST_SERVER_CATCH_LINE, value=f"", inline=False)
            catch_embed.add_field(name=CREATURE_FIRST_SERVER_CATCH_LINE, value=f"", inline=False)
            total_xp += 10000
        if self.creature.local_rarity == MYTHICAL:
            self.add_xp_field_to_embed(name=MYTHICAL_CATCH_LINE, value=f"", inline=False)
            catch_embed.add_field(name=MYTHICAL_CATCH_LINE, value=f"", inline=False)
            total_xp += 10000

        return total_xp, catch_embed

    def add_xp_field_to_embed(self, name, value, inline):
        self.xp_fields.append(
            {
                'name': name,
                'value': value,
                'inline': inline
            }
        )
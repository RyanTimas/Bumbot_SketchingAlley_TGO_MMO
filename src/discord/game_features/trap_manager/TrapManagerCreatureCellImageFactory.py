from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, get_centered_text_position, get_centered_image_position
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.file_paths import *


class TrapManagerCreatureCellImageFactory:
    def __init__(self, creature:TGOCreature=None):
        self.creature = creature

    def generate_creature_cell_image(self):
        creature_cell_image = Image.open(TRAP_MANAGER_CAPTURES_CREATURE_ICON_OVERLAY_IMAGE)
        creature_image = self.creature.creature_image.resize((130, 100), Image.LANCZOS)
        creature_cell_image.paste(creature_image, get_centered_image_position(foreground_image=creature_image, background_image=creature_cell_image, center_pixel= (70, 37)))
        return self.add_text_to_image(creature_cell_image)

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        # ADD SPECIES NAME TO IMAGE
        species_name = self.creature.full_name
        font = resize_text_to_fit(text=f"{species_name}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 12), max_width=126, min_font_size=8)
        draw.text(get_centered_text_position(text=f"{species_name}", font=font, center_pixel_location=(70, 94)), f"{species_name}", fill=(0, 0, 0), font=font)

        # CATCH DATE TO IMAGE
        # todo: convert to MMM DD, YYYY HH:MM AM/PM format
        catch_date = self.creature.catch_time
        font = resize_text_to_fit(text=f"{catch_date}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 13), max_width=126, min_font_size=8)
        draw.text(get_centered_text_position(text=f"{catch_date}", font=font, center_pixel_location=(70, 110)), f"{catch_date}", fill=(0, 0, 0), font=font)

        # ADD ENVIRONMENT TO IMAGE
        environment_name = get_tgommo_db_handler().get_environment_by_id(self.creature.environment_id).name
        font = resize_text_to_fit(text=f"{environment_name}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 10), max_width=126, min_font_size=8)
        draw.text(get_centered_text_position(text=f"{environment_name}", font=font, center_pixel_location=(70, 140)), f"{environment_name}", fill=(0, 0, 0), font=font)


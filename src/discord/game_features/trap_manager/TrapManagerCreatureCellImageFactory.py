from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, get_centered_text_position, get_centered_image_position, \
    convert_date_format_to_month_name
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_TRAP_MANAGER_OFF_GREEN, \
    FONT_COLOR_TRAP_MANAGER_OFF_BROWN, FONT_COLOR_TRAP_MANAGER_FOREST_GREEN
from src.resources.constants.file_paths import *


class TrapManagerCreatureCellImageFactory:
    def __init__(self, creature:TGOCreature=None):
        self.creature = creature

    def generate_creature_cell_image(self):
        creature_cell_image = Image.open(f"{TRAP_MANAGER_OVERLAY_CAPTURES_CREATURE_ICON_BG_BASE}_{self.creature.local_rarity.name}{IMAGE_FILE_EXTENSION}")
        creature_cell_image_overlay = Image.open(TRAP_MANAGER_CAPTURES_CREATURE_ICON_OVERLAY_IMAGE)

        # prepare creature image
        creature_image = self.creature.creature_image.resize((130, 100), Image.LANCZOS)
        creature_cell_image.paste(creature_image, get_centered_image_position(foreground_image=creature_image, background_image=creature_cell_image, center_pixel= (70, 54)), creature_image)

        # add overlay to image
        creature_cell_image.paste(creature_cell_image_overlay, (0, 0), creature_cell_image_overlay)

        return self.add_text_to_image(creature_cell_image)

    def add_text_to_image(self, base_image: Image):
        draw = ImageDraw.Draw(base_image)

        # ADD SPECIES NAME TO IMAGE
        species_name = self.creature.full_name
        font = resize_text_to_fit(text=f"{species_name}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 12), max_width=126, min_font_size=8)
        draw.text(get_centered_text_position(text=f"{species_name}", font=font, center_pixel_location=(70, 9)), f"{species_name}", fill=self.creature.local_rarity.font_color, font=font)

        # ADD CATCH DATE TO IMAGE
        catch_date, catch_time = convert_date_format_to_month_name(date_str=self.creature.caught_date, input_format="%Y-%d-%m %H:%M:%S", include_time=True, split_date_time=True)
        font = resize_text_to_fit(text=f"{catch_date}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 13), max_width=126, min_font_size=8)
        draw.text(get_centered_text_position(text=f"{catch_date}", font=font, center_pixel_location=(70, 110)), f"{catch_date}", fill=FONT_COLOR_TRAP_MANAGER_FOREST_GREEN, font=font)
        # ADD CATCH TIME TO IMAGE
        font = resize_text_to_fit(text=f"{catch_time}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 13), max_width=126, min_font_size=8)
        draw.text(get_centered_text_position(text=f"{catch_time}", font=font, center_pixel_location=(70, 124)), f"{catch_time}", fill=FONT_COLOR_TRAP_MANAGER_FOREST_GREEN, font=font)


        # ADD ENVIRONMENT TO IMAGE
        environment_name = get_tgommo_db_handler().get_environment_by_id(self.creature.environment_id).name
        font = resize_text_to_fit(text=f"{environment_name}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 10), max_width=126, min_font_size=8)
        draw.text(get_centered_text_position(text=f"{environment_name}", font=font, center_pixel_location=(70, 140)), f"{environment_name}", fill=FONT_COLOR_TRAP_MANAGER_OFF_BROWN, font=font)
        return base_image


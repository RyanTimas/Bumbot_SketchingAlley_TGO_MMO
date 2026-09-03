from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, get_centered_text_position, get_centered_image_position, \
    convert_date_format_to_month_name
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_TRAP_MANAGER_OFF_GREEN, \
    FONT_COLOR_TRAP_MANAGER_OFF_BROWN, FONT_COLOR_TRAP_MANAGER_FOREST_GREEN, \
    OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_CAUGHT, OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT, \
    OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_SERVER, OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_ENVIRONMENT, DAY
from src.resources.constants.file_paths import *


print_type_map = {
    OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_CAUGHT: OMNIPOTENT_BAIT_MANAGER_CREATURE_ICON_CAUGHT_PRINT_IMAGE,
    OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_ENVIRONMENT: OMNIPOTENT_BAIT_MANAGER_CREATURE_ICON_ENVIRONMENT_PRINT_IMAGE,
    OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_SERVER: OMNIPOTENT_BAIT_MANAGER_CREATURE_ICON_CAUGHT_SERVER_IMAGE,
    OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT: OMNIPOTENT_BAIT_MANAGER_CREATURE_ICON_UNCAUGHT_PRINT_IMAGE
}

class OmnipotentBaitManagerCreatureCellImageFactory:
    def __init__(self, creature:TGOCreature=None, active_environment=None):
        self.creature = creature
        self.active_environment = active_environment

    def generate_creature_cell_image(self):
        creature_cell_image = Image.open(f"{OMNIPOTENT_BAIT_MANAGER_CREATURE_ICON_BASE_IMAGE}")
        creature_cell_image_overlay = Image.open(f"{OMNIPOTENT_BAIT_MANAGER_CREATURE_ICON_OVERLAY_IMAGE}")
        creature_cell_border_image = Image.open(f"{OMNIPOTENT_BAIT_MANAGER_CREATURE_ICON_BORDER_BASE}_{self.creature.local_rarity.name}{IMAGE_FILE_EXTENSION}")
        creature_cell_print_image = Image.open(print_type_map[self.creature.caught_type])

        creature_image = self.creature.creature_image.resize((206, 160), Image.LANCZOS)

        environments_foler_path = os.path.join(IMAGE_FOLDER_ENVIRONMENTS_PATH, self.active_environment.short_name, self.creature.sub_environment, f"{self.creature.sub_environment}{self.active_environment.local_img_suffix}_{DAY}{IMAGE_FILE_EXTENSION}")
        environment_bg_image = Image.open(environments_foler_path).resize((540, 304), Image.LANCZOS)

        # prepare creature image
        creature_cell_image.paste(environment_bg_image, get_centered_image_position(foreground_image=environment_bg_image, background_image=creature_cell_image, center_pixel=(122, 86)), environment_bg_image)
        creature_cell_image.paste(creature_image, get_centered_image_position(foreground_image=creature_image, background_image=creature_cell_image, center_pixel=(122, 86)), creature_image)

        creature_cell_image.paste(creature_cell_image_overlay, (0, 0), creature_cell_image_overlay)
        creature_cell_image.paste(creature_cell_border_image, (0, 0), creature_cell_border_image)
        creature_cell_image.paste(creature_cell_print_image, (0, 0), creature_cell_print_image)

        return self.add_text_to_image(creature_cell_image)

    def add_text_to_image(self, base_image: Image):
        draw = ImageDraw.Draw(base_image)

        # ADD SPECIES NAME TO IMAGE
        species_name = self.creature.name
        font = resize_text_to_fit(text=f"{species_name}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 20), max_width=156, min_font_size=8)
        draw.text((82, 162), f"{species_name}", fill=self.creature.local_rarity.font_color, font=font)

        # ADD SPECIES FULL NAME TO IMAGE
        species_full_name = self.creature.full_name
        font = resize_text_to_fit(text=f"{species_full_name}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 12), max_width=156, min_font_size=8)
        draw.text((82, 182), f"{species_full_name}", fill=self.creature.local_rarity.font_color, font=font)

        return base_image


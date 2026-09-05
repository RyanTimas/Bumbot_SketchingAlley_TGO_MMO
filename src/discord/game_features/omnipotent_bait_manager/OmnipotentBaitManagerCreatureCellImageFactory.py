from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, get_centered_text_position, get_centered_image_position, convert_int_to_letter, set_image_opacity, convert_image_to_silhouette
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import *
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

        creature_image = self.get_creature_image_based_on_catch_type()

        environment_bg_image = Image.open(os.path.join(IMAGE_FOLDER_ENVIRONMENTS_PATH, self.active_environment.short_name, self.creature.sub_environment, f"{self.creature.sub_environment}{self.active_environment.local_img_suffix}_{DAY}{IMAGE_FILE_EXTENSION}")).resize((540, 304), Image.LANCZOS)
        environment_color_overlay = self.add_rarity_overlay(base_image=environment_bg_image, opacity=0.7)

        # prepare creature image
        creature_cell_image.paste(environment_bg_image, get_centered_image_position(foreground_image=environment_bg_image, background_image=creature_cell_image, center_pixel=(122, 86)), environment_bg_image)
        creature_cell_image.paste(environment_color_overlay, get_centered_image_position(foreground_image=environment_color_overlay, background_image=creature_cell_image, center_pixel=(122, 86)), environment_color_overlay)
        creature_cell_image.paste(creature_image, get_centered_image_position(foreground_image=creature_image, background_image=creature_cell_image, center_pixel=(122, 86)), creature_image)

        creature_cell_image.paste(creature_cell_image_overlay, (0, 0), creature_cell_image_overlay)
        creature_cell_image.paste(creature_cell_border_image, (0, 0), creature_cell_border_image)
        creature_cell_image.paste(creature_cell_print_image, (0, 0), creature_cell_print_image)

        return self.add_text_to_image(creature_cell_image)

    def add_rarity_overlay(self, base_image: Image, opacity: float = 0.05) -> Image:
        overlay_img =  Image.new("RGBA", base_image.size, (self.creature.local_rarity.color.r, self.creature.local_rarity.color.g, self.creature.local_rarity.color.b) if self.creature.caught_type != OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT else (255, 255, 255))
        overlay_img = set_image_opacity(overlay_img, opacity)
        return overlay_img

    def get_creature_image_based_on_catch_type(self):
        creature_img = self.creature.creature_image
        if self.creature.caught_type == OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_ENVIRONMENT:
            creature_img = set_image_opacity(creature_img, 0.8)
        elif self.creature.caught_type == OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_SERVER:
            creature_img = convert_image_to_silhouette(creature_img)
        elif self.creature.caught_type == OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT:
            creature_img = Image.open(FALLBACK_CREATURE_IMAGE)

        return creature_img.resize((206, 160), Image.LANCZOS)


    def add_text_to_image(self, base_image: Image):
        draw = ImageDraw.Draw(base_image)

        # ADD SPECIES NAME TO IMAGE
        species_name = self.creature.name if self.creature.caught_type != OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT else "???"
        font = resize_text_to_fit(text=f"{species_name}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 20), max_width=156, min_font_size=8)
        draw.text((82, 162), f"{species_name}", fill=self.creature.local_rarity.font_color, font=font)

        # ADD SPECIES FULL NAME TO IMAGE
        species_full_name = self.creature.full_name if self.creature.caught_type != OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT else "???"
        font = resize_text_to_fit(text=f"{species_full_name}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 12), max_width=156, min_font_size=8)
        draw.text((82, 182), f"{species_full_name}", fill=self.creature.local_rarity.font_color, font=font)

        # ADD SPECIES NUMBER TO IMAGE
        font = resize_text_to_fit(text=f"{self.creature.local_dex_no}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 30), max_width=156, min_font_size=8)
        draw.text(get_centered_text_position(text=f"{self.creature.local_dex_no}", font=font, center_pixel_location=(28, 20)), f"{self.creature.local_dex_no}", fill=FONT_COLOR_BLACK, font=font)

        # ADD VARIANT NUMBER TO IMAGE (IF APPROPRIATE)
        if self.creature.variant_no > 1:
            variant_letter = convert_int_to_letter(self.creature.variant_no)
            font = resize_text_to_fit(text=f"{variant_letter}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 20), max_width=156, min_font_size=8)
            draw.text(get_centered_text_position(text=f"{variant_letter}", font=font, center_pixel_location=(60, 12)), f"{variant_letter}", fill=FONT_COLOR_BLACK, font=font)

        return base_image


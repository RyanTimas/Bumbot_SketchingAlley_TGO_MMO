from PIL import ImageDraw, ImageFont, Image

from src.commons.CommonFunctions import get_image_path
from src.discord.objects import TGOCreature
from src.discord.objects.CreatureRarity import TRANSCENDANT
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class EncyclopediaIconFactory:
    def __init__(self, creature = None, total_catches=0, total_mythical_catches=0, rarity =TGOMMO_RARITY_COMMON, creature_is_locked=True, show_stats=False):
        self.creature: TGOCreature = creature
        self.total_catches = total_catches
        self.total_mythical_catches = total_mythical_catches

        self.dex_no = f'{"0" if self.creature.dex_no <10 else ""}{self.creature.dex_no}'

        self.creature_is_locked = creature_is_locked
        self.show_stats = False if creature_is_locked else show_stats

        self.rarity = rarity


    def generate_dex_entry_image(self):
        # Create a copy of the background to serve as the canvas
        dex_icon_img = Image.open(f"{DEX_ICON_BACKGROUND_BASE}_{self.creature.rarity.name}{IMAGE_FILE_EXTENSION}")

        # Paste the shadow onto the final image
        shadow_img = Image.open(DEX_ICON_SHADOW_IMAGE)
        dex_icon_img.paste(shadow_img, (0, 0), shadow_img)

        # Paste the creature icon onto the final image
        creature_icon_img = Image.open(DEX_ICON_CREATURE_LOCKED_ICON_IMAGE) if self.creature_is_locked else self.creature.dex_icon_image
        dex_icon_img.paste(creature_icon_img, (0, 0), creature_icon_img)

        if self.show_stats:
            icon_stats_overlay = Image.open(DEX_ICON_STATS_BAR_IMAGE)
            dex_icon_img.paste(icon_stats_overlay, (0, 0), icon_stats_overlay)

        # add the final overlay on top
        icon_overlay = Image.open(DEX_ICON_OVERLAY if self.creature.rarity.name != TRANSCENDANT.name else DEX_ICON_TRANSCENDANT_OVERLAY)
        dex_icon_img.paste(icon_overlay, (0, 0), icon_overlay)

        # self.add_text_to_image(image=dex_icon_img).show()
        return self.add_text_to_image(image=dex_icon_img)


    def add_text_to_image(self, image: Image):
        if self.creature.name == TRANSCENDANT.name:
            return image

        image = self.add_dex_num_to_image(image)

        if self.show_stats:
            image = self.add_stats_to_image(image)
        return image
    def add_stats_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)
        stats_num_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 12)

        # Draw the total catches
        draw.text((81, 64), f"{self.total_catches}", fill=(0, 0, 0), font=stats_num_font, anchor="mm")
        draw.text((58, 64), f"{self.total_mythical_catches}", fill=(255, 255, 255), font=stats_num_font, anchor="mm")
        return image
    def add_dex_num_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)
        dex_num_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 26)
        # dex_num_font = load_font(font_path=get_image_path(FONT_FOREST_BOLD_FILE, IMAGE_FOLDER_FONTS), font_size=26)

        # Center X position
        x_center, y_center = 15, 38

        # Get actual height of each character to calculate precise positioning
        char_heights = []
        for digit in self.dex_no:
            bbox = dex_num_font.getbbox(digit)
            height = bbox[3] - bbox[1]
            char_heights.append(height)

        # Calculate vertical offset to center all characters around y_center
        num_chars = len(self.dex_no)
        line_height = 26  # Roughly the height of each character with font size 26
        total_height = line_height * num_chars
        start_y = y_center - (total_height / 2) + (line_height / 2)

        # Draw each digit on a new line
        for i, digit in enumerate(self.dex_no):
            # Position each character vertically
            y = start_y + (i * line_height)
            draw.text((x_center, y), digit, fill=(0, 0, 0), font=dex_num_font, anchor="mm")

        return image
from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, get_centered_text_position, get_centered_image_position
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE
from src.resources.constants.file_paths import *


class ItemUnlockImageFactory:
    def __init__(self, item):
        self.item = item

    def generate_item_unlock_image(self):
        # Create a copy of the background to serve as the canvas
        unlocked_avatar_img = Image.open(UNLOCKED_AVATAR_BACKGROUND_IMAGE)
        unlocked_avatar_img.paste(self.item.item_image, get_centered_image_position(foreground_image=self.item.item_image, background_image=unlocked_avatar_img), self.item.item_image)

        return self.add_text_to_image(image=unlocked_avatar_img)

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        # ADD "item unlocked" TITLE TO IMAGE
        text = "Item Unlocked"
        font = resize_text_to_fit(text=text, draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 24), max_width=1200, min_font_size=7)
        draw.text(get_centered_text_position(text=text, font=font, center_pixel_location=(640, 564)), text, fill=FONT_COLOR_WHITE, font=font)

        # ADD ITEM NAME TO IMAGE
        text = self.item.item_name
        font = resize_text_to_fit(text=text, draw=draw, font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 64), max_width=1200, min_font_size=7)
        draw.text(get_centered_text_position(text=text, font=font, center_pixel_location=(640, 632)), text, fill=FONT_COLOR_WHITE, font=font)
        return image


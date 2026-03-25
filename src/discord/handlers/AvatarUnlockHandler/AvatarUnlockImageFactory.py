from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, center_text_on_pixel
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE
from src.resources.constants.file_paths import *


class AvatarUnlockImageFactory:
    def __init__(self, avatar):
        self.avatar = avatar

    def generate_avatar_quest_tab_image(self):
        # Create a copy of the background to serve as the canvas
        unlocked_avatar_img = Image.open(UNLOCKED_AVATAR_BACKGROUND_IMAGE)
        unlocked_avatar_img.paste(self.avatar.avatar_image, (0, 0), self.avatar.avatar_image)

        return self.add_text_to_image(image=unlocked_avatar_img)

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        # ADD "avatar unlocked" TITLE TO IMAGE
        text = "Avatar Unlocked"
        font = resize_text_to_fit(text=text, draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 24), max_width=1200, min_font_size=7)
        draw.text(center_text_on_pixel(text=text, font=font, center_pixel_location=(640, 564)), text, fill=FONT_COLOR_WHITE, font=font)

        # ADD AVATAR NAME TO IMAGE
        text = self.avatar.name
        font = resize_text_to_fit(text=text, draw=draw, font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 64), max_width=1200, min_font_size=7)
        draw.text(center_text_on_pixel(text=text, font=font, center_pixel_location=(640, 632)), text, fill=FONT_COLOR_WHITE, font=font)

        # todo: add unlock condition text to image

        return image


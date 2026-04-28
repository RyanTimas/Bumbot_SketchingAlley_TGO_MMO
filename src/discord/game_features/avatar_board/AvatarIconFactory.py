from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit
from src.resources.constants.file_paths import *


class AvatarIconFactory:
    def __init__(self, avatar):
        self.avatar = avatar

    def generate_avatar_quest_tab_image(self):
        # Create a copy of the background to serve as the canvas
        white_border_img = Image.open(AVATAR_UNLOCKED_AVATAR_TAB_BORDER_IMAGE)
        avatar_background_img = Image.open(f"{AVATAR_BOARD_UNLOCKED_AVATAR_BACKGROUND_BASE}_{self.avatar.avatar_type}{IMAGE_FILE_EXTENSION}")

        avatar_background_img.paste(self.avatar.avatar_thumbnail_image, (0, 0), self.avatar.avatar_thumbnail_image)
        avatar_background_img.paste(white_border_img, (0, 0), white_border_img)

        self.add_text_to_image(image=avatar_background_img)
        return avatar_background_img

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 12)
        font = resize_text_to_fit(text=self.avatar.name, draw=draw, font=font, max_width=58, min_font_size=7)

        # Draw the total catches
        draw.text((35,75), f"{self.avatar.name}", fill=(0, 0, 0), font=font, anchor="mm")
        return image


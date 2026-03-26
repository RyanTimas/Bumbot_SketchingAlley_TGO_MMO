import random

from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, get_centered_text_position, get_centered_image_position
from src.discord.objects.TGOAvatar import TGOAvatar
from src.discord.objects.TGOPlayerItem import TGOPlayerItem
from src.resources.constants.file_paths import *


class ShopItemImageFactory:
    def __init__(self, avatar:TGOAvatar=None, item:TGOPlayerItem=None):
        self.avatar = avatar
        self.item = item

        self.is_shop_item_avatar = self.avatar is not None



    def generate_shop_item_image(self):
        # Create a copy of the background to serve as the canvas
        display_case_image = Image.open(SHOP_TROPHY_CASE_IMAGE if self.is_shop_item_avatar else SHOP_ITEM_CASE_IMAGE)
        display_case_overlay_image = Image.open(SHOP_ITEM_CASE_OVERLAY_IMAGE)
        display_case_price_tag_image = Image.open(SHOP_ITEM_CASE_PRICE_TAG_IMAGE)

        item_image = self.avatar.avatar_image.resize((924, 520), Image.LANCZOS) if self.is_shop_item_avatar else self.item.item_image.resize((300, 300), Image.LANCZOS)
        pixel_coordinates = get_centered_image_position(foreground_image=item_image, background_image=display_case_image, center_pixel=(250, 332))
        display_case_image.paste(item_image, pixel_coordinates, item_image)

        display_case_image.paste(display_case_overlay_image, (0, 0), display_case_overlay_image)
        display_case_image.paste(display_case_price_tag_image, (0, 0), display_case_price_tag_image)

        return self.add_text_to_image(display_case_image)

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        # ADD PRICE TO IMAGE
        temp_price = random.randint(100, 500)
        font = resize_text_to_fit(text=f"{temp_price}", draw=draw, font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 28), max_width=95, min_font_size=7)
        draw.text(get_centered_text_position(text=f"{temp_price}", font=font, center_pixel_location=(125, 137)), f"{temp_price}", fill=(0, 0, 0), font=font)

        # Add Price to Image
        # font = resize_text_to_fit(text=f"{self.avatar.shop_price}", draw=draw, font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 28), max_width=95, min_font_size=7)
        # draw.text(center_text_on_pixel(text=f"{self.avatar.shop_price}", font=font, center_pixel_location=(125, 137)), f"{self.avatar.name}", fill=(0, 0, 0), font=font)
        # return image

        # ADD NAME TO IMAGE
        name = self.avatar.name if self.is_shop_item_avatar else self.item.item_name
        font = resize_text_to_fit(text=name, draw=draw, font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 28), max_width=220, min_font_size=7)
        draw.text(get_centered_text_position(text=name, font=font, center_pixel_location=(332, 137)), name, fill=(0, 0, 0), font=font)
        return image


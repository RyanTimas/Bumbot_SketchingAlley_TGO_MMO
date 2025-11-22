from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import center_text_on_pixel, resize_text_to_fit, resize_text_to_fit_with_newlines
from src.discord.objects.TGOPlayerItem import TGOPlayerItem
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE
from src.resources.constants.file_paths import *


class ItemInventoryIconImageFactory:
    def __init__(self, item: TGOPlayerItem):
        self.item = item

    def generate_inventory_icon_image(self):
        dex_icon_img = Image.open(ITEM_INVENTORY_TAB_BG_IMAGE)
        item_img = Image.open(f"{ITEM_INVENTORY_ITEM_BASE}{self.item.img_root}{IMAGE_FILE_EXTENSION}").resize((64, 64))

        dex_icon_img.paste(item_img, (5, 5), item_img)
        return self.add_text_to_image(image=dex_icon_img)


    def add_text_to_image(self, image: Image.Image):
        draw = ImageDraw.Draw(image)
        max_width = 300

        # add item name to image
        image_name_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 20)
        image_name_font = resize_text_to_fit(text=self.item.item_name, draw=draw, font=image_name_font, max_width=max_width, min_font_size=12)
        draw.text((72, 5), text=self.item.item_name, font=image_name_font, fill=FONT_COLOR_WHITE)

        # add item description to image
        image_description_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 12)
        item_description_font, item_description_text  = resize_text_to_fit_with_newlines(text=self.item.item_description, draw=draw, font=image_description_font, max_width=max_width, min_font_size=12, allow_newlines=True)
        draw.text((75, 25), text=item_description_text, font=item_description_font, fill=FONT_COLOR_WHITE)

        # add item uses to image
        item_use_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 26)
        item_use_font = resize_text_to_fit(text= f'{self.item.item_quantity}', draw=draw, font=item_use_font, max_width=32, min_font_size=6)
        pixel_location = center_text_on_pixel(text= f'{self.item.item_quantity}', font=item_use_font, center_pixel_location=(476, 36))
        draw.text(pixel_location, text= f'{self.item.item_quantity}', font=item_use_font, fill=FONT_COLOR_WHITE)

        return image



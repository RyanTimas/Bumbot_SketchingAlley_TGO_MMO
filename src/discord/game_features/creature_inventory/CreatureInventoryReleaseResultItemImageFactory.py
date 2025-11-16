from PIL import Image, ImageDraw, ImageFont
from pygments.lexer import default

from src.commons.CommonFunctions import center_text_on_pixel, resize_text_to_fit
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOPlayerItem import TGOPlayerItem
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_BLACK, TGOMMO_RARITY_MYTHICAL
from src.resources.constants.file_paths import *


class CreatureInventoryReleaseResultItemImageFactory:
    def __init__(self, item: TGOPlayerItem, count: int):
        self.item = item
        self.count = count

    def generate_release_result_item_icon_image(self):
        tab_img = Image.open(CREATURE_INVENTORY_RELEASE_SUMMARY_TAB_BG_IMAGE)
        item_img = Image.open(ITEM_INVENTORY_ITEM_ROOT + f"_{self.item.item_type}_{self.item.rarity.name}" + IMAGE_FILE_EXTENSION).resize((100, 100))
        tab_img.paste(item_img, (31, 12), item_img)

        return self.add_text_to_image(image=tab_img)


    def add_text_to_image(self, image: Image.Image):
        draw = ImageDraw.Draw(image)
        max_width = 300

        # add item name to image
        item_name_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 35)
        item_name_font = resize_text_to_fit(text=self.item.item_name, draw=draw, font=item_name_font, max_width=max_width, min_font_size=8)
        pixel_location = center_text_on_pixel(text= self.item.item_name, font=item_name_font, center_pixel_location=(412, 66))
        draw.text(pixel_location, text=self.item.item_name, font=item_name_font, fill=FONT_COLOR_BLACK)

        # add item count to image
        count_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 50)
        pixel_location = center_text_on_pixel(text= f"{self.count}", font=count_font, center_pixel_location=(742, 62))
        draw.text(pixel_location, text=f"{self.count}", font=count_font, fill=FONT_COLOR_BLACK)

        return image
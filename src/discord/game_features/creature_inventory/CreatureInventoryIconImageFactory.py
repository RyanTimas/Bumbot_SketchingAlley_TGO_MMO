from PIL import Image, ImageDraw, ImageFont
from pygments.lexer import default

from src.commons.CommonFunctions import center_text_on_pixel, resize_text_to_fit
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_BLACK, TGOMMO_RARITY_MYTHICAL
from src.resources.constants.file_paths import *


class CreatureInventoryIconImageFactory:
    def __init__(self, creature: TGOCreature):
        self.creature = creature

    def generate_inventory_icon_image(self):
        icon_img = Image.new('RGBA', (80, 144), (0, 0, 0, 0))

        dex_icon_background = Image.open(DEX_ICON_BACKGROUND_BASE + f"_{self.creature.kingdom}" + IMAGE_FILE_EXTENSION)
        dex_icon_overlay = Image.open(CREATURE_INVENTORY_INDIVIDUAL_CREATURE_TAB_WHITE_BORDER_IMAGE)
        creature_img = Image.open(DEX_ICON_CREATURE_BASE + f"_{self.creature.img_root}" + f"{"_S" if self.creature.rarity.name == TGOMMO_RARITY_MYTHICAL else ""}" + IMAGE_FILE_EXTENSION)

        icon_img.paste(dex_icon_background, (-22, 2), dex_icon_background)
        icon_img.paste(creature_img, (-22, 2), creature_img)
        icon_img.paste(dex_icon_overlay, (0, 0), dex_icon_overlay)

        if self.creature.is_favorite:
            favorite_overlay = Image.open(CREATURE_INVENTORY_INDIVIDUAL_CREATURE_FAVORITE_STAMP_IMAGE)
            creature_img.paste(favorite_overlay, (0, 0), favorite_overlay)

        return self.add_text_to_image(image=icon_img)


    def add_text_to_image(self, image: Image.Image):
        draw = ImageDraw.Draw(image)
        default_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 23)

        nickname_font = resize_text_to_fit(text=self.creature.nickname, draw=draw, font=default_font, max_width=68, min_font_size=8)
        pixel_location = center_text_on_pixel(text= self.creature.nickname, font=nickname_font, center_pixel_location=(40, 80))
        draw.text(pixel_location, text=self.creature.nickname, font=nickname_font, fill=FONT_COLOR_BLACK)

        species_font = resize_text_to_fit(text=self.creature.full_name, draw=draw, font=default_font, max_width=68, min_font_size=6)
        pixel_location = center_text_on_pixel(text= self.creature.full_name, font=species_font, center_pixel_location=(40, 92))
        draw.text(pixel_location, text=self.creature.full_name, font=species_font, fill=FONT_COLOR_BLACK)

        catch_id_font = resize_text_to_fit(text= f'{self.creature.catch_id}', draw=draw, font=default_font, max_width=68, min_font_size=6)
        pixel_location = center_text_on_pixel(text= f'{self.creature.catch_id}', font=catch_id_font, center_pixel_location=(40, 110))
        draw.text(pixel_location, text= f'{self.creature.catch_id}', font=catch_id_font, fill=FONT_COLOR_BLACK)

        indicator_text = ""
        if self.creature.nickname != '':
            indicator_text += "❗"
        if self.creature.rarity.name == TGOMMO_RARITY_MYTHICAL:
            indicator_text += "✨"

        indicator_font = resize_text_to_fit(text= indicator_text, draw=draw, font=default_font, max_width=68, min_font_size=6)
        pixel_location = center_text_on_pixel(text= indicator_text, font=indicator_font, center_pixel_location=(40, 129))
        draw.text(pixel_location, text= indicator_text, font=indicator_font, fill=FONT_COLOR_BLACK)

        return image



from PIL import ImageDraw, ImageFont, Image

from src.commons.CommonFunctions import get_image_path
from src.discord.objects import TGOCreature
from src.discord.objects.CreatureRarity import TRANSCENDANT
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class EncyclopediaLocationIndexIconFactory:
    def __init__(self, environment = None, user_unique_catches= None, possible_unique_catches= None,):
        self.environment: TGOEnvironment = environment
        self.user_unique_catches = user_unique_catches if user_unique_catches else [0, 0, 0]
        self.possible_unique_catches = possible_unique_catches if possible_unique_catches else [0, 0, 0]


    def generate_location_tab_icon_image(self):
        # Create a copy of the background to serve as the canvas
        location_tab_icon_overlay_img = Image.open(ENCYCLOPEDIA_LOCATION_INDEX_OVERLAY_IMAGE)
        location_tab_icon_empty_stars_img = Image.open(ENCYCLOPEDIA_LOCATION_INDEX_EMPTY_STARS_IMAGE)
        location_tab_icon_environment_bg_img = Image.open(f"{ENCYCLOPEDIA_LOCATION_INDEX_ENVIRONMENT_BG_IMAGE_BASE}_{self.environment.dex_no}{IMAGE_FILE_EXTENSION}")

        location_tab_icon_img = location_tab_icon_environment_bg_img
        location_tab_icon_img.paste(location_tab_icon_empty_stars_img, (0, 0), location_tab_icon_empty_stars_img)
        location_tab_icon_img.paste(location_tab_icon_overlay_img, (0, 0), location_tab_icon_overlay_img)

        # add stars if user has caught all possible unique catches
        if self.possible_unique_catches[0] == self.user_unique_catches[0]:
            location_tab_icon_star_1_img = Image.open(ENCYCLOPEDIA_LOCATION_INDEX_STAR_1_MAGE)
            location_tab_icon_img.paste(location_tab_icon_star_1_img, (0, 0), location_tab_icon_star_1_img)
        # star 2 for variants
        if self.possible_unique_catches[1] == self.user_unique_catches[1]:
            location_tab_icon_star_2_img = Image.open(ENCYCLOPEDIA_LOCATION_INDEX_STAR_2_MAGE)
            location_tab_icon_img.paste(location_tab_icon_star_2_img, (0, 0), location_tab_icon_star_2_img)
        # star 3 for mythicals
        if self.possible_unique_catches[2] == self.user_unique_catches[2]:
            location_tab_icon_star_3_img = Image.open(ENCYCLOPEDIA_LOCATION_INDEX_STAR_3_MAGE)
            location_tab_icon_img.paste(location_tab_icon_star_3_img, (0, 0), location_tab_icon_star_3_img)

        # self.add_text_to_image(image=dex_icon_img).show()
        return self.add_text_to_image(image=location_tab_icon_img)


    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        draw.text((10, 3), f"{self.environment.name}", fill=(0, 0, 0), font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 12), anchor="lt")
        draw.text((10, 16), f"{self.environment.location}", fill=(0, 0, 0), font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 10), anchor="lt")
        draw.text((10, 36), f"{self.user_unique_catches[0]} / {self.possible_unique_catches[0]}", fill=(0, 0, 0), font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 12), anchor="lt")

        return image
from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, center_text_on_pixel
from src.discord.objects import TGOPlayer
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_BLACK
from src.resources.constants.file_paths import *


class PlayerProfileSidePanelTabFactory:
    def __init__(self, tab_type: str, player: TGOPlayer, content_image_path: str = None, background_image_path: str = None, image_color_path: str = None, tab_title: str = None, tab_subtitle: str = None, tab_footer: str = None):
        self.player = player
        self.tab_type = tab_type

        self.content_image_path = content_image_path
        self.background_image_path = background_image_path
        self.image_color_path = image_color_path

        self.tab_title = tab_title
        self.tab_subtitle = tab_subtitle
        self.tab_footer = tab_footer

    def create_tab(self):
        # create base tab image based off of background color
        tab_image = Image.open(f'{self.image_color_path}')

        tab_overlay_image = Image.open(PLAYER_PROFILE_SIDE_PANEL_TABS_OVERLAY_IMAGE)
        tab_overlay_shadow_image = Image.open(PLAYER_PROFILE_SIDE_PANEL_TABS_OVERLAY_SHADOW_IMAGE)
        tab_shadow_image = Image.open(PLAYER_PROFILE_SIDE_PANEL_TABS_BG_SHADOW_IMAGE)
        tab_empty_stars_image = Image.open(PLAYER_PROFILE_SIDE_PANEL_TABS_EMPTY_STARS_IMAGE)

        tab_image.paste(tab_shadow_image, (0, 0), tab_shadow_image)

        tab_content_image = Image.open(self.content_image_path)
        # tab_background_image = Image.open(self.background_image_path)

        tab_image.paste(tab_overlay_shadow_image, (0, 0), tab_overlay_shadow_image)
        tab_image.paste(tab_content_image, (-22, 3), tab_content_image)
        tab_image.paste(tab_overlay_image, (0, 0), tab_overlay_image)

        if self.tab_type == 'Biomes' or self.tab_type == 'Collections':
            tab_image.paste(tab_empty_stars_image, (0, 0), tab_empty_stars_image)
            #todo: handle stars

        tab_image = self.place_text_on_tab(tab_image=tab_image)

        return tab_image

    def place_text_on_tab(self, tab_image: Image.Image):
        draw = ImageDraw.Draw(tab_image)

        # place title text
        base_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 20)
        font = resize_text_to_fit(text=self.tab_title, draw=draw, font=base_font, max_width=100, min_font_size=10)
        pixel_location = center_text_on_pixel(text=self.tab_title, font=font, center_pixel_location=(130, 17))
        draw.text(pixel_location, text=self.tab_title, font=font, fill=FONT_COLOR_BLACK)

        # place subtitle text
        base_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 12)
        font = resize_text_to_fit(text=self.tab_subtitle, draw=draw, font=base_font, max_width=100, min_font_size=5)
        pixel_location = center_text_on_pixel(text=self.tab_subtitle, font=font, center_pixel_location=(130, 42))
        draw.text(pixel_location, text=self.tab_subtitle, font=font, fill=FONT_COLOR_BLACK)

        if self.tab_type == 'Team':
            # place footer text
            base_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 12)
            font = resize_text_to_fit(text=self.tab_footer, draw=draw, font=base_font, max_width=100, min_font_size=10)
            pixel_location = center_text_on_pixel(text=self.tab_footer, font=font, center_pixel_location=(130, 72))
            draw.text(pixel_location, text=self.tab_footer, font=font, fill=FONT_COLOR_BLACK)

        return tab_image
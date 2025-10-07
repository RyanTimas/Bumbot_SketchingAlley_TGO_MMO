from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, center_text_on_pixel, get_query_connector
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects import TGOPlayer
from src.discord.objects.TGOCollection import TGOCollection
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_BLACK
from src.resources.constants.file_paths import *


class PlayerProfileSidePanelTabFactory:
    def __init__(self, tab_type: str, player: TGOPlayer, collection: TGOCollection = None, content_image_path: str = None, background_image_path: str = None, image_color_path: str = None, tab_title: str = None, tab_subtitle: str = None, tab_footer: str = None):
        self.player = player
        self.collection = collection

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
            self.place_stars_on_tab(tab_image=tab_image)

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

    def place_stars_on_tab(self, tab_image: Image.Image):
        remove_variants_suffix = ' c.variant_no=1;'

        caught_query = self.collection.caught_count_query[:-1] + f"{get_query_connector(self.collection.caught_count_query)}{remove_variants_suffix}" if 'variant_no' not in self.collection.caught_count_query else self.collection.caught_count_query
        total_query = self.collection.total_count_query[:-1] + f"{get_query_connector(self.collection.total_count_query)}{remove_variants_suffix}" if 'variant_no' not in self.collection.total_count_query else self.collection.total_count_query

        caught_number = get_tgommo_db_handler().execute_query(caught_query, params=(self.player.user_id,))[0][0]
        total_number = get_tgommo_db_handler().execute_query(total_query, params=())[0][0]

        filter_mythics_suffix = ' uc.is_mythical=1;'

        caught_number_mythics = get_tgommo_db_handler().execute_query(self.collection.caught_count_query[:-1] + f"{get_query_connector(self.collection.total_count_query)}{filter_mythics_suffix}", params=(self.player.user_id,))[0][0]

        caught_number_variants = get_tgommo_db_handler().execute_query(self.collection.caught_count_query, params=(self.player.user_id,))[0][0]
        total_number_variants = get_tgommo_db_handler().execute_query(self.collection.total_count_query, params=())[0][0]

        if caught_number == total_number:
            first_star_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_TABS_STARS_IMAGE_BASE}_1{IMAGE_FILE_EXTENSION}")
            tab_image.paste(first_star_image, (0, 0), first_star_image)
        if caught_number_variants == total_number_variants:
            second_star_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_TABS_STARS_IMAGE_BASE}_2{IMAGE_FILE_EXTENSION}")
            tab_image.paste(second_star_image, (0, 0), second_star_image)
        if caught_number_mythics == total_number:
            third_star_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_TABS_STARS_IMAGE_BASE}_3{IMAGE_FILE_EXTENSION}")
            tab_image.paste(third_star_image, (0, 0), third_star_image)

        return tab_image
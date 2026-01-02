from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import convert_to_png, resize_text_to_fit, build_user_profile_pic
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.encyclopedia_location_index.EncyclopediaLocationIndexIconFactory import EncyclopediaLocationIndexIconFactory
from src.discord.objects.TGOEnvironment import NATIONAL_ENV
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE
from src.resources.constants.file_paths import *


class EncyclopediaLocationIndexImageFactory:
    def __init__(self, user = None, ):
        self.user = user
        self.player = get_tgommo_db_handler().get_user_profile_by_user_id(user.id, convert_to_object=True) if user else None

        self.locations = []
        self.location_icons = []
        self.page_num = 1
        self.total_pages = 1


    def build_encyclopedia_location_index_page_image(self, new_page_number = None):
        # set new values in case button was clicked
        self.page_num = new_page_number if new_page_number is not None else self.page_num

        # construct base layers, start with environment bg
        encyclopedia_img = Image.open(f"{ENCOUNTER_SCREEN_ENVIRONMENT_BG_BASE}{IMAGE_FILE_EXTENSION}")
        overlay_img = Image.open(ENCYCLOPEDIA_OVERLAY_IMAGE)
        textbox_shadow_img = Image.open(ENCYCLOPEDIA_TEXT_SHADOW_IMAGE)
        corner_overlay_img = Image.open(ENCYCLOPEDIA_CORNER_OVERLAY_SERVER_IMAGE if not self.player else ENCYCLOPEDIA_CORNER_OVERLAY_USER_IMAGE)
        location_tab_icon_corkboard_img = Image.open(ENCYCLOPEDIA_LOCATION_INDEX_CORKBOARD_MAGE)

        if self.player:
            profile_pic = build_user_profile_pic(self.user)
            encyclopedia_img.paste(profile_pic, (60, 0), profile_pic)

        # place layers on final image
        encyclopedia_img.paste(textbox_shadow_img, (0, 0), textbox_shadow_img)
        encyclopedia_img.paste(overlay_img, (0, 0), overlay_img)
        encyclopedia_img.paste(location_tab_icon_corkboard_img, (0, 0), location_tab_icon_corkboard_img)
        encyclopedia_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)

        # add dex section to image
        encyclopedia_img = self.build_location_index_section(encyclopedia_img)

        # add text to image
        encyclopedia_img = self.add_text_to_encyclopedia_image(encyclopedia_img)

        return encyclopedia_img

    def build_location_index_section(self, encyclopedia_img: Image):
        # generate dex icons
        self.location_icons = self.get_location_icons()
        icons_grid = self.create_location_index_grid(self.location_icons)

        # add bottom bar
        encyclopedia_img = self.build_bottom_bar(encyclopedia_img)

        encyclopedia_img.paste(icons_grid, (800, 170), icons_grid)
        return encyclopedia_img

    # create a grid of dex icons
    def create_location_index_grid(self, icons):
        # Create a blank canvas for the grid
        grid_width, grid_height = 300, 410
        grid_canvas = Image.new('RGBA', (grid_width, grid_height), (0, 0, 0, 0))

        # Define grid parameters
        icon_width, icon_height = 300, 50
        icons_per_row = 1  # 500 / 100 = 5, but we need padding

        # Calculate padding
        horizontal_padding = 0
        vertical_padding = 10

        # Place icons in grid
        row, col = 0, 0
        for i, icon in enumerate(icons):
            # Calculate position
            x = col * (icon_width + horizontal_padding if i != 0 else 0)
            y = row * (icon_height + vertical_padding if i != 0 else 0)

            # Paste icon onto canvas
            grid_canvas.paste(icon, (int(x), int(y)))

            # Move to next position
            col += 1
            if col >= icons_per_row:
                col = 0
                row += 1

            # Stop if we run out of space
            if row * (icon_height + vertical_padding) + icon_height > grid_height:
                break
        return grid_canvas

    # return list of all dex icons for species
    def get_location_icons(self, page_swap = 0):
        if len(self.locations) == 0:
            self.page_num = 1
            self.locations = get_tgommo_db_handler().get_all_environments_in_rotation()
            self.locations.insert(0, NATIONAL_ENV)

        self.page_num += page_swap

        imgs = []
        raw_imgs = []

        total_icons_per_page = 8
        starting_index = (self.page_num - 1) * total_icons_per_page  # Adjust calculation to start from 0
        ending_index = min(starting_index + total_icons_per_page, len(self.locations))  # Ensure we don't go past the end of the list

        # Only process within our page range
        for i in range(starting_index, ending_index):
            location = self.locations[i]
            user_catches, possible_catches = get_tgommo_db_handler().get_environment_catch_stats_for_user(user_id=None if not self.player else self.player.user_id, environment_id=location.environment_id)

            icon = EncyclopediaLocationIndexIconFactory(environment=location, user_unique_catches=user_catches, possible_unique_catches=possible_catches)
            icon_img = icon.generate_location_tab_icon_image()

            raw_imgs.append(icon_img)
            imgs.append(convert_to_png(icon_img, f'location_icon_{location.name}_{location.variant_name}.png'))

        # in the case the amount of dex icons has changed, we need to update the total pages and reset to page 1
        if self.total_pages != (len(self.locations) // total_icons_per_page) + (1 if len(self.locations) % total_icons_per_page > 0 else 0):
            self.total_pages = (len(self.locations) // total_icons_per_page) + (1 if len(self.locations) % total_icons_per_page > 0 else 0)

        return raw_imgs


    # build user's profile pic from discord id
    def build_bottom_bar(self, encyclopedia_img: Image):
        bottom_bar_img = Image.open(ENCYCLOPEDIA_BOTTOM_BAR_IMAGE)
        bottom_bar_back_arrow_img = Image.open(ENCYCLOPEDIA_BOTTOM_BACK_ARROW_IMAGE if self.page_num > 1 else ENCYCLOPEDIA_BOTTOM_BACK_ARROW_IMAGE_DISABLED)
        bottom_bar_forward_arrow_img = Image.open(ENCYCLOPEDIA_BOTTOM_FORWARD_ARROW_IMAGE if self.page_num < self.total_pages else ENCYCLOPEDIA_BOTTOM_FORWARD_ARROW_IMAGE_DISABLED)
        bottom_bar_environment_icon_img = Image.open(ENCYCLOPEDIA_BOTTOM_ENVIRONMENT_ICON_IMAGE)

        encyclopedia_img.paste(bottom_bar_img, (0, 0), bottom_bar_img)

        encyclopedia_img.paste(bottom_bar_back_arrow_img, (0, 0), bottom_bar_back_arrow_img)
        encyclopedia_img.paste(bottom_bar_forward_arrow_img, (0, 0), bottom_bar_forward_arrow_img)

        # encyclopedia_img.paste(bottom_bar_environment_icon_img, (0, 0), bottom_bar_environment_icon_img)

        return encyclopedia_img


    def add_text_to_encyclopedia_image(self, encyclopedia_img: Image):
        draw = ImageDraw.Draw(encyclopedia_img)

        name_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 50)
        tag_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 30)
        bar_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 22)

        # NAME TEXT
        text = f"Sketching Alley" if not self.player else self.player.nickname
        font = resize_text_to_fit(text=text, draw=draw, font=name_font, max_width=475, min_font_size=10)
        pixel_location = (70, 535)
        draw.text(pixel_location, text= text, font=font, fill=FONT_COLOR_WHITE)

        if self.player:
            text = f"@{self.user.name}"
            font = resize_text_to_fit(text=text, draw=draw, font=tag_font, max_width=260, min_font_size=10)
            pixel_location = (83, 593)
            draw.text(pixel_location, text= text, font=font, fill=FONT_COLOR_WHITE)

        # BOTTOM BAR TEXT
        # text = f"{self.environment.name} | {'Night' if self.environment.is_night_environment else 'Day'}"
        # font = resize_text_to_fit(text=text, draw=draw, font=bar_font, max_width=225, min_font_size=10)
        # pixel_location = center_text_on_pixel(text, bar_font, center_pixel_location=(980, 630))
        # draw.text(pixel_location, text=text, font=font, color=bar_font_color)

        return encyclopedia_img

from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import convert_to_png, get_user_discord_profile_pic, center_text_on_pixel, \
    resize_text_to_fit, build_user_profile_pic
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.encyclopedia.EncyclopediaIconFactory import EncyclopediaIconFactory
from src.discord.objects.CreatureRarity import TRANSCENDANT, MYTHICAL
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE, FONT_COLOR_DARK_GRAY, NIGHT, DAY, BOTH
from src.resources.constants.file_paths import *


class EncyclopediaImageFactory:
    def __init__(self, environment: TGOEnvironment, message_author= None, target_user= None, is_verbose= False, show_variants= False, show_mythics= False, time_of_day= BOTH):
        self.environment = environment
        self.message_author = message_author
        self.target_user = target_user
        self.target_user_id = None if not self.target_user else self.target_user.id

        self.is_verbose = is_verbose
        self.show_variants = show_variants
        self.show_mythics = show_mythics
        self.time_of_day = time_of_day

        self.total_user_catches, self.distinct_user_catches = get_tgommo_db_handler().get_user_catch_totals_for_environment(user_id=self.target_user_id, include_variants=self.show_variants, include_mythics=self.show_mythics, environment=self.environment, time_of_day=self.time_of_day)
        self.creatures = []
        self.dex_icons = []
        self.page_num = 1
        self.total_pages = 1

        self.load_relevant_info(show_variants= show_variants, show_mythics= show_mythics, time_of_day= time_of_day)


    def load_relevant_info(self, is_verbose= None, show_variants= None, show_mythics= None, time_of_day= None, new_page_number= None):
        self.is_verbose = self.is_verbose if is_verbose is None else is_verbose

        self.page_num = self.page_num if new_page_number is None else new_page_number
        self.show_variants = self.show_variants if show_variants is None else show_variants
        self.show_mythics = self.show_mythics if show_mythics is None else show_mythics
        self.time_of_day = time_of_day if time_of_day else self.time_of_day

        self.page_num = 1 if show_variants or show_mythics or time_of_day else self.page_num

        # if any of these values changed, we need to reload the creatures list
        if show_variants is not None or show_mythics is not None or time_of_day is not None or new_page_number:
            self.total_user_catches, self.distinct_user_catches = get_tgommo_db_handler().get_user_catch_totals_for_environment(user_id=self.target_user_id, include_variants=self.show_variants, include_mythics=self.show_mythics, environment=self.environment, time_of_day=self.time_of_day)
            self.creatures = get_tgommo_db_handler().get_creatures_to_display_for_encyclopedia(environment_id=self.environment.dex_no, environment_variant_type=self.time_of_day, include_variants=self.show_variants)
        if show_variants is not None or show_mythics is not None or time_of_day is not None or new_page_number or is_verbose is not None:
            self.dex_icons = self.get_dex_icons()

    def build_encyclopedia_page_image(self, is_verbose = None, show_variants = None, show_mythics= None, time_of_day= None, new_page_number = None):
        # set new values in case button was clicked
        self.load_relevant_info(is_verbose=is_verbose, show_variants= show_variants, show_mythics= show_mythics, time_of_day= time_of_day, new_page_number= new_page_number)

        # construct base layers, start with environment bg
        encyclopedia_img = Image.open(f"{ENCOUNTER_SCREEN_ENVIRONMENT_BG_BASE}{IMAGE_FILE_EXTENSION}")
        overlay_img = Image.open(ENCYCLOPEDIA_OVERLAY_IMAGE)
        textbox_shadow_img = Image.open(ENCYCLOPEDIA_TEXT_SHADOW_IMAGE)
        corner_overlay_img = Image.open(ENCYCLOPEDIA_CORNER_OVERLAY_SERVER_IMAGE if self.target_user else ENCYCLOPEDIA_CORNER_OVERLAY_USER_IMAGE)

        # load user profile pic if not server page
        if self.target_user:
            profile_pic = build_user_profile_pic(user= self.target_user)
            encyclopedia_img.paste(profile_pic, (60, 0), profile_pic)

        # place layers on final image
        encyclopedia_img.paste(textbox_shadow_img, (0, 0), textbox_shadow_img)
        encyclopedia_img.paste(overlay_img, (0, 0), overlay_img)
        encyclopedia_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)
        encyclopedia_img = self.build_dex_section(encyclopedia_img)

        return self.add_text_to_encyclopedia_image(encyclopedia_img)
    def build_dex_section(self, encyclopedia_img: Image):
        if self.show_mythics:
            mythical_overlay_img = Image.open(ENCYCLOPEDIA_OVERLAY_SHINY_IMAGE)
            encyclopedia_img.paste(mythical_overlay_img, (0, 0), mythical_overlay_img)

        # generate dex icons
        icons_grid = self.create_dex_icons_grid()

        # add bottom bar and top bar
        encyclopedia_img = self.build_encyclopedia_dex_top_bar(encyclopedia_img)
        encyclopedia_img = self.build_encyclopedia_dex_bottom_bar(encyclopedia_img)

        encyclopedia_img.paste(icons_grid, (694, 142), icons_grid)
        return encyclopedia_img


    # create a grid of dex icons
    def create_dex_icons_grid(self):
        # Create a blank canvas for the grid
        grid_canvas = Image.new('RGBA', (520, 535), (0, 0, 0, 0))

        # Define grid parameters
        icon_width, icon_height = 100, 75
        icons_per_row = 5  # 500 / 100 = 5, but we need padding

        # Calculate padding
        horizontal_padding = 3
        vertical_padding = 20

        # Place icons in grid
        row, col = 0, 0
        for i, dex_icon in enumerate(self.dex_icons):
            # Open the file as an image

            # Calculate position
            x = col * (icon_width + horizontal_padding if i != 0 else 0)
            y = row * (icon_height + vertical_padding if i != 0 else 0)

            # Paste icon onto canvas
            grid_canvas.paste(dex_icon, (int(x), int(y)))

            # Move to next position
            col += 1
            if col >= icons_per_row:
                col = 0
                row += 1

            # Stop if we run out of space
            if row * (icon_height + vertical_padding) + icon_height > 500:
                break

        return grid_canvas

    # return list of all dex icons for species
    def get_dex_icons(self, page_swap = 0):
        self.page_num += page_swap

        imgs = []
        raw_imgs = []

        starting_index = (self.page_num - 1) * 25  # Adjust calculation to start from 0
        ending_index = min(starting_index + 25, len(self.creatures))  # Ensure we don't go past the end of the list

        # Only process creatures within our page range
        for i in range(starting_index, ending_index):
            creature: TGOCreature = self.creatures[i]
            total_catches_for_species, total_mythical_catches_for_species = get_tgommo_db_handler().get_total_catches_for_species(creature=creature, user_id=self.target_user_id, environment_dex_no=self.environment.dex_no, environment_variant_no=self.time_of_day, group_variants=not self.show_variants)
            creature_is_locked = total_mythical_catches_for_species == 0 if self.show_mythics else total_catches_for_species == 0

           # if creature is locked and is transcendant, skip it & don't display the icon
            if not (creature_is_locked and creature.default_rarity.name == TRANSCENDANT.name):
                dex_icon_img = self.build_dex_icon(creature=creature, total_catches=total_catches_for_species, total_mythical_catches=total_mythical_catches_for_species, creature_is_locked=creature_is_locked)
                raw_imgs.append(dex_icon_img)
                imgs.append(convert_to_png(dex_icon_img, f'creature_icon_{creature.name}_{creature.variant_name}.png'))

        # in the case the amount of dex icons has changed, we need to update the total pages and reset to page 1
        if self.total_pages != (len(self.creatures) // 25) + (1 if len(self.creatures) % 25 > 0 else 0):
            self.total_pages = (len(self.creatures) // 25) + (1 if len(self.creatures) % 25 > 0 else 0)

        return raw_imgs  #, imgs

    def build_dex_icon(self, creature: TGOCreature, total_catches: int, total_mythical_catches: int, creature_is_locked: bool):
        if self.show_mythics and creature.local_rarity.name != TRANSCENDANT.name:
            creature.set_creature_rarity(MYTHICAL)
        if not self.show_variants:
            first_caught_variant = get_tgommo_db_handler().get_first_caught_variant_for_creature(creature_dex_no=creature.dex_no, user_id=self.target_user_id, environment_dex_no=self.environment.dex_no)
            if first_caught_variant != 1:
                creature.variant_no = get_tgommo_db_handler().get_first_caught_variant_for_creature(creature_dex_no=creature.dex_no, user_id=self.target_user_id, environment_dex_no=self.environment.dex_no)
                creature.define_creature_images()

        dex_icon = EncyclopediaIconFactory(creature=creature, environment=self.environment, total_catches=total_catches, total_mythical_catches=total_mythical_catches, creature_is_locked=creature_is_locked, show_stats=self.is_verbose)
        return dex_icon.generate_dex_entry_image()


    def build_encyclopedia_dex_top_bar(self, encyclopedia_img: Image):
        top_bar_img = Image.open(ENCYCLOPEDIA_TOP_BAR_IMAGE if not self.show_mythics else ENCYCLOPEDIA_TOP_BAR_SHINY_IMAGE)
        top_bar_camera_img = Image.open(ENCYCLOPEDIA_TOP_BAR_CAMERA_ICON_IMAGE)
        top_bar_encounter_img = Image.open(ENCYCLOPEDIA_TOP_BAR_ENCOUNTER_ICON_IMAGE)

        encyclopedia_img.paste(top_bar_img, (0, 0), top_bar_img)
        encyclopedia_img.paste(top_bar_camera_img, (0, 0), top_bar_camera_img)
        encyclopedia_img.paste(top_bar_encounter_img, (0, 0), top_bar_encounter_img)

        return encyclopedia_img
    def build_encyclopedia_dex_bottom_bar(self, encyclopedia_img: Image):
        bottom_bar_img = Image.open(ENCYCLOPEDIA_BOTTOM_BAR_IMAGE if not self.show_mythics else ENCYCLOPEDIA_BOTTOM_BAR_SHINY_IMAGE)
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
        text = f"Sketching Alley" if not self.target_user else self.target_user.display_name
        font = resize_text_to_fit(text=text, draw=draw, font=name_font, max_width=475, min_font_size=10)
        pixel_location = (70, 535)
        draw.text(pixel_location, text= text, font=font, fill=FONT_COLOR_WHITE)

        if self.target_user:
            text = f"@{self.target_user.name}"
            font = resize_text_to_fit(text=text, draw=draw, font=tag_font, max_width=260, min_font_size=10)
            pixel_location = (83, 593)
            draw.text(pixel_location, text= text, font=font, fill=FONT_COLOR_WHITE)

        # TOP BAR TEXT
        bar_font_color = FONT_COLOR_DARK_GRAY if self.show_mythics else FONT_COLOR_WHITE
        creature_count = len([creature for creature in self.creatures if creature.local_rarity.name != TRANSCENDANT.name])

        text = f"{'0' if self.distinct_user_catches < 10 else ''} {self.distinct_user_catches} / {'0' if creature_count < 10 else ''} {creature_count}"
        pixel_location = center_text_on_pixel(text, bar_font, center_pixel_location=(858, 109))
        draw.text(pixel_location, text= text, font=bar_font, fill=bar_font_color)

        text = f"{self.total_user_catches}"
        pixel_location = center_text_on_pixel(text, bar_font, center_pixel_location=(1082, 109))
        draw.text(pixel_location, text=text, font=bar_font, fill=bar_font_color)

        # BOTTOM BAR TEXT
        # text = f"{self.environment.name} | {'Night' if self.environment.is_night_environment else 'Day'}"
        # font = resize_text_to_fit(text=text, draw=draw, font=bar_font, max_width=225, min_font_size=10)
        # pixel_location = center_text_on_pixel(text, bar_font, center_pixel_location=(980, 630))
        # draw.text(pixel_location, text=text, font=font, color=bar_font_color)

        return encyclopedia_img
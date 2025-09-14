from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

from src.commons.CommonFunctions import convert_to_png, get_user_discord_profile_pic, center_text_on_pixel, \
    resize_text_to_fit
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.image_factories.DexIconFactory import DexIconFactory
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE, FONT_COLOR_DARK_GRAY
from src.resources.constants.file_paths import *


class EncyclopediaImageFactory:
    def __init__(self, environment: TGOEnvironment, verbose = False, show_variants = False, show_mythics = False, is_server_page = False, user = None):
        self.environment = environment
        self.is_server_page = is_server_page
        self.user = user
        self.verbose = verbose
        self.show_mythics = show_mythics

        self.creatures = []
        self.total_catches = None
        self.distinct_catches = None
        self.show_variants = show_variants

        self.dex_icons = []
        self.creatures = []
        self.page_num = 1
        self.total_pages = 1


    def load_relevant_info(self):
        encyclopedia_info = get_tgommo_db_handler().get_encyclopedia_page_info(user_id=self.user.id, is_server_page=self.is_server_page, include_variants=self.show_variants, include_mythics=self.show_mythics)

        self.total_catches = encyclopedia_info[0]
        self.distinct_catches = encyclopedia_info[1]


    def build_encyclopedia_page_image(self, new_page_number = None, is_verbose = None, show_variants = None, show_mythics = None):
        # set new values in case button was clicked
        self.page_num = new_page_number if new_page_number is not None else self.page_num
        self.verbose = is_verbose if is_verbose is not None else self.verbose
        self.show_variants = show_variants if show_variants is not None else self.show_variants
        self.show_mythics = show_mythics if show_mythics is not None else self.show_mythics
        if show_variants is not None or show_mythics is not None:
            self.creatures = []

        # construct base layers, start with environment bg
        encyclopedia_img = Image.open(f"{ENCYCLOPEDIA_BG_BASE}_{self.environment.environment_id}.png")
        overlay_img = Image.open(ENCYCLOPEDIA_OVERLAY_IMAGE)
        textbox_shadow_img = Image.open(ENCYCLOPEDIA_TEXT_SHADOW_IMAGE)
        corner_overlay_img = Image.open(ENCYCLOPEDIA_CORNER_OVERLAY_SERVER_IMAGE if self.is_server_page else ENCYCLOPEDIA_CORNER_OVERLAY_USER_IMAGE)

        if not self.is_server_page:
            profile_pic = self.build_user_profile_pic()
            encyclopedia_img.paste(profile_pic, (60, 0), profile_pic)


        # place layers on final image
        encyclopedia_img.paste(textbox_shadow_img, (0, 0), textbox_shadow_img)
        encyclopedia_img.paste(overlay_img, (0, 0), overlay_img)
        encyclopedia_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)

        # add dex section to image
        encyclopedia_img = self.build_dex_section(encyclopedia_img)

        # add text to image
        encyclopedia_img = self.add_text_to_encyclopedia_image(encyclopedia_img)

        return encyclopedia_img


    def build_dex_section(self, encyclopedia_img: Image.Image):
        if self.show_mythics:
            mythical_overlay_img = Image.open(ENCYCLOPEDIA_OVERLAY_SHINY_IMAGE)
            encyclopedia_img.paste(mythical_overlay_img, (0, 0), mythical_overlay_img)

        # generate dex icons
        self.dex_icons = self.get_dex_icons()
        icons_grid = self.create_dex_icons_grid(self.dex_icons)

        # add bottom bar and top bar
        encyclopedia_img = self.build_encyclopedia_dex_top_bar(encyclopedia_img)
        encyclopedia_img = self.build_encyclopedia_dex_bottom_bar(encyclopedia_img)

        encyclopedia_img.paste(icons_grid, (694, 142), icons_grid)
        return encyclopedia_img


    # create a grid of dex icons
    def create_dex_icons_grid(self, dex_icons):
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
        for i, dex_icon in enumerate(dex_icons):
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
        if len(self.creatures) == 0:
            self.load_relevant_info()
            self.page_num = 1
            self.creatures = get_tgommo_db_handler().get_all_creatures_caught_by_user(user_id=self.user.id, include_variants=self.show_variants, is_server_page=self.is_server_page, include_mythics=self.show_mythics)

        self.page_num += page_swap

        imgs = []
        raw_imgs = []

        starting_index = (self.page_num - 1) * 25  # Adjust calculation to start from 0
        ending_index = min(starting_index + 25, len(self.creatures))  # Ensure we don't go past the end of the list

        # Only process creatures within our page range
        for i in range(starting_index, ending_index):
            creature = self.creatures[i]
            creature_name = creature[1]
            variant_name = creature[2]
            dex_no = creature[3]
            variant_no = creature[4] if len(creature) == 8 else  creature[8][0]
            rarity = get_tgommo_db_handler().get_creature_rarity_for_environment(creature_id=creature[0], environment_id=1)
            total_catches = creature[5]
            total_mythical_catches = creature[6]
            img_root = creature[7]

            creature_is_locked = total_mythical_catches == 0 if self.show_mythics else total_catches == 0

            dex_icon = DexIconFactory(creature_name=creature_name, dex_no=dex_no, variant_no=variant_no, rarity=rarity,creature_is_locked=creature_is_locked, show_stats=self.verbose, total_catches=total_catches, total_mythical_catches=total_mythical_catches, show_mythics=self.show_mythics, img_root=img_root)
            dex_icon_img = dex_icon.generate_dex_entry_image()

            raw_imgs.append(dex_icon_img)
            imgs.append(convert_to_png(dex_icon_img, f'creature_icon_{creature[3]}_{variant_no}.png'))


        # in the case the amount of dex icons has changed, we need to update the total pages and reset to page 1
        if self.total_pages != (len(self.creatures) // 25) + (1 if len(self.creatures) % 25 > 0 else 0):
            self.total_pages = (len(self.creatures) // 25) + (1 if len(self.creatures) % 25 > 0 else 0)

        return raw_imgs  #, imgs


    # build user's profile pic from discord id
    def build_user_profile_pic(self):
        # get user's profile pic
        profile_pic_avatar_url = get_user_discord_profile_pic(self.user)
        response = requests.get(profile_pic_avatar_url)

        profile_pic = Image.open(BytesIO(response.content)).convert("RGBA")
        profile_pic = profile_pic.resize((600, 600), Image.LANCZOS)

        # profile_pic = self.add_blur_mask_to_image(profile_pic)

        return profile_pic


    def build_encyclopedia_dex_top_bar(self, encyclopedia_img: Image.Image):
        top_bar_img = Image.open(ENCYCLOPEDIA_TOP_BAR_IMAGE if not self.show_mythics else ENCYCLOPEDIA_TOP_BAR_SHINY_IMAGE)
        top_bar_camera_img = Image.open(ENCYCLOPEDIA_TOP_BAR_CAMERA_ICON_IMAGE)
        top_bar_encounter_img = Image.open(ENCYCLOPEDIA_TOP_BAR_ENCOUNTER_ICON_IMAGE)

        encyclopedia_img.paste(top_bar_img, (0, 0), top_bar_img)
        encyclopedia_img.paste(top_bar_camera_img, (0, 0), top_bar_camera_img)
        encyclopedia_img.paste(top_bar_encounter_img, (0, 0), top_bar_encounter_img)

        return encyclopedia_img


    def build_encyclopedia_dex_bottom_bar(self, encyclopedia_img: Image.Image):
        bottom_bar_img = Image.open(ENCYCLOPEDIA_BOTTOM_BAR_IMAGE if not self.show_mythics else ENCYCLOPEDIA_BOTTOM_BAR_SHINY_IMAGE)
        bottom_bar_back_arrow_img = Image.open(ENCYCLOPEDIA_BOTTOM_BACK_ARROW_IMAGE if self.page_num > 1 else ENCYCLOPEDIA_BOTTOM_BACK_ARROW_IMAGE_DISABLED)
        bottom_bar_forward_arrow_img = Image.open(ENCYCLOPEDIA_BOTTOM_FORWARD_ARROW_IMAGE if self.page_num < self.total_pages else ENCYCLOPEDIA_BOTTOM_FORWARD_ARROW_IMAGE_DISABLED)
        bottom_bar_environment_icon_img = Image.open(ENCYCLOPEDIA_BOTTOM_ENVIRONMENT_ICON_IMAGE)

        encyclopedia_img.paste(bottom_bar_img, (0, 0), bottom_bar_img)

        encyclopedia_img.paste(bottom_bar_back_arrow_img, (0, 0), bottom_bar_back_arrow_img)
        encyclopedia_img.paste(bottom_bar_forward_arrow_img, (0, 0), bottom_bar_forward_arrow_img)

        # encyclopedia_img.paste(bottom_bar_environment_icon_img, (0, 0), bottom_bar_environment_icon_img)

        return encyclopedia_img


    def add_text_to_encyclopedia_image(self, encyclopedia_img: Image.Image):
        draw = ImageDraw.Draw(encyclopedia_img)

        name_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 50)
        tag_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 30)
        bar_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 22)

        # NAME TEXT
        text = f"Sketching Alley" if self.is_server_page else self.user.display_name
        font = resize_text_to_fit(text=text, draw=draw, font=name_font, max_width=475, min_font_size=10)
        pixel_location = (70, 535)
        draw.text(pixel_location, text= text, font=font, fill=FONT_COLOR_WHITE)

        if not self.is_server_page:
            text = f"@{self.user.name}"
            font = resize_text_to_fit(text=text, draw=draw, font=tag_font, max_width=260, min_font_size=10)
            pixel_location = (83, 593)
            draw.text(pixel_location, text= text, font=font, fill=FONT_COLOR_WHITE)

        # TOP BAR TEXT
        bar_font_color = FONT_COLOR_DARK_GRAY if self.show_mythics else FONT_COLOR_WHITE
        text = f"{'0' if self.distinct_catches < 10 else ''} {self.distinct_catches} / {'0' if len(self.creatures) < 10 else ''} {len(self.creatures)}"
        pixel_location = center_text_on_pixel(text, bar_font, center_pixel_location=(858, 109))
        draw.text(pixel_location, text= text, font=bar_font, fill=bar_font_color)

        text = f"{self.total_catches}"
        pixel_location = center_text_on_pixel(text, bar_font, center_pixel_location=(1082, 109))
        draw.text(pixel_location, text=text, font=bar_font, fill=bar_font_color)

        # BOTTOM BAR TEXT
        # text = f"{self.environment.name} | {'Night' if self.environment.is_night_environment else 'Day'}"
        # font = resize_text_to_fit(text=text, draw=draw, font=bar_font, max_width=225, min_font_size=10)
        # pixel_location = center_text_on_pixel(text, bar_font, center_pixel_location=(980, 630))
        # draw.text(pixel_location, text=text, font=font, color=bar_font_color)

        return encyclopedia_img


    def get_total_pages(self):
        return self.total_pages


    def get_current_page(self):
        return self.page_num

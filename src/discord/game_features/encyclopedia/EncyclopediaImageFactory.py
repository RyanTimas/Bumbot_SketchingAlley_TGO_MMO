from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import convert_to_png, get_centered_text_position, resize_text_to_fit, build_user_profile_pic
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.encyclopedia.EncyclopediaIconFactory import EncyclopediaIconFactory
from src.discord.game_features.encyclopedia.encyclopedia_xl.EncyclopediaXLImageFactory import EncyclopediaXLImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.discord.objects.CreatureRarity import TRANSCENDANT, MYTHICAL
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOEnvironment import TGOEnvironment
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE, FONT_COLOR_DARK_GRAY, NIGHT, DAY, BOTH
from src.resources.constants.file_paths import *


class EncyclopediaImageFactory(BaseImageFactory):
    def __init__(self, environment: TGOEnvironment, message_author=None, target_user=None):
        super().__init__(message_author=message_author, target_user=target_user)

        self.environment = environment
        self.is_verbose = False
        self.show_variants = False
        self.show_mythics = False

        self.time_of_day = BOTH
        self.rarity_filter = None
        self.creature_class_filter = None

        self.is_xl_mode = False
        self.encyclopedia_xl_image_factory = EncyclopediaXLImageFactory(parent_image_factory=self)

        self.total_user_catches = 0
        self.unique_catches_for_user = 0
        self.unique_creatures_available_for_environment = 0

        self.creatures = []
        self.dex_icons = []


    def reload_image(self, target_user=None, environment=None, new_page_number = None, is_verbose = None, show_variants = None, show_mythics= None, time_of_day= None, is_xl_mode = None, rarity = None, creature_class = None):
        self.load_relevant_info(target_user=target_user, environment=environment if environment != self.environment else None, is_verbose=is_verbose if is_verbose != self.is_verbose else None, show_variants= show_variants if show_variants != self.show_variants else None, show_mythics= show_mythics if show_mythics != self.show_mythics else None, time_of_day= time_of_day  if time_of_day != self.time_of_day else None, rarity=rarity, creature_class=creature_class,  is_xl_mode= is_xl_mode if is_xl_mode != self.is_xl_mode else None, new_page_number= new_page_number if new_page_number != self.page_num else None)
        return self.build_image()

    def load_relevant_info(self, target_user=None, environment=None, is_verbose= None, show_variants= None, show_mythics= None, time_of_day= None, is_xl_mode= None, new_page_number= None, rarity = None, creature_class = None):
        self.target_user = target_user if target_user is not None else self.target_user
        self.environment = environment if environment is not None else self.environment
        self.is_xl_mode = is_xl_mode if is_xl_mode is not None else self.is_xl_mode

        self.page_num = 1 if any(param is not None for param in [show_variants, time_of_day, environment, rarity, creature_class]) else new_page_number if new_page_number else self.page_num

        # basic filter options
        self.is_verbose = is_verbose if is_verbose is not None else self.is_verbose
        self.show_variants = show_variants if show_variants is not None else self.show_variants
        self.show_mythics = show_mythics if show_mythics is not None else self.show_mythics

        # deluxe filter options
        self.time_of_day = time_of_day if time_of_day is not None else self.time_of_day
        self.rarity_filter = None if rarity == "None" else (rarity if rarity is not None else self.rarity_filter)
        self.creature_class_filter = None if creature_class == "None" else (creature_class if creature_class is not None else self.creature_class_filter)

        data_changed = any(param is not None for param in [target_user, environment, show_variants, show_mythics, time_of_day, rarity, creature_class])
        if data_changed:
            self.is_server_view = self.target_user.user_id == 0
            self.total_user_catches = get_tgommo_db_handler().get_total_catches_base(user_id=self.target_user.user_id, include_variants=self.show_variants, is_mythical=self.show_mythics, environment_dex_no=self.environment.dex_no, time_of_day=self.time_of_day, rarity=self.rarity_filter, creature_class=self.creature_class_filter)
            self.unique_catches_for_user = get_tgommo_db_handler().get_unique_catches_base(user_id=self.target_user.user_id, include_variants=self.show_variants, is_mythical=self.show_mythics, environment_dex_no=self.environment.dex_no, time_of_day=self.time_of_day, rarity=self.rarity_filter, creature_class=self.creature_class_filter)
            self.unique_creatures_available_for_environment = get_tgommo_db_handler().get_total_unique_creatures_available_for_environment(environment_dex_no=self.environment.dex_no, include_variants=self.show_variants, time_of_day=self.time_of_day, rarity=self.rarity_filter, creature_class=self.creature_class_filter)

            self.creatures = get_tgommo_db_handler().get_creatures_to_display_for_encyclopedia(environment_id=self.environment.dex_no, environment_variant_type=self.time_of_day, include_variants=self.show_variants, rarity=self.rarity_filter, creature_class=self.creature_class_filter)
        if data_changed or is_verbose is not None:
            self.dex_icons = self.get_dex_icons()

    def build_image(self):
        if self.is_xl_mode:
            return self.encyclopedia_xl_image_factory.reload_image()

        # construct base layers, start with environment bg
        encyclopedia_img = Image.open(f"{ENCOUNTER_SCREEN_ENVIRONMENT_BG_BASE}{IMAGE_FILE_EXTENSION}")
        overlay_img = Image.open(ENCYCLOPEDIA_OVERLAY_IMAGE)
        textbox_shadow_img = Image.open(ENCYCLOPEDIA_TEXT_SHADOW_IMAGE)
        corner_overlay_img = Image.open(ENCYCLOPEDIA_CORNER_OVERLAY_SERVER_IMAGE if self.is_server_view else ENCYCLOPEDIA_CORNER_OVERLAY_USER_IMAGE)

        # load user profile pic if not server page
        if not self.is_server_view:
            profile_pic = build_user_profile_pic(user= self.target_user.discord_profile)
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
        elif self.time_of_day != BOTH:
            time_overlay_img = Image.open(ENCYCLOPEDIA_OVERLAY_NIGHT_IMAGE if self.time_of_day == NIGHT else ENCYCLOPEDIA_OVERLAY_DAY_IMAGE)
            encyclopedia_img.paste(time_overlay_img, (0, 0), time_overlay_img)

        # generate dex icons
        starting_index = (self.page_num - 1) * 25  # Adjust calculation to start from 0
        ending_index = min(starting_index + 25, len(self.creatures))  # Ensure we don't go past the end of the list
        icons_grid = self.build_grid(icons=self.dex_icons[starting_index: ending_index], grid_size=(520, 535), icon_size=(100, 75), icons_per_page=25, icons_per_row=5, horizontal_padding=3, vertical_padding=20)

        # add bottom bar and top bar
        encyclopedia_img = self.build_encyclopedia_dex_top_bar(encyclopedia_img)
        encyclopedia_img = self.build_encyclopedia_dex_bottom_bar(encyclopedia_img)

        encyclopedia_img.paste(icons_grid, (694, 142), icons_grid)
        return encyclopedia_img

    # return list of all dex icons for species
    def get_dex_icons(self, page_swap = 0):
        self.page_num += page_swap

        imgs = []
        raw_imgs = []

        # Only process creatures within our page range
        for i, creature in enumerate(self.creatures):
            total_catches_for_creature_for_environment = get_tgommo_db_handler().get_total_catches_for_species_for_environment(user_id=self.target_user.user_id, creature_dex_no=creature.dex_no if not self.show_variants else None, creature_id=creature.creature_id  if self.show_variants else None, environment_dex_no=self.environment.dex_no, time_of_day=self.time_of_day)
            total_mythical_catches_for_species = get_tgommo_db_handler().get_total_catches_for_species_for_environment(user_id=self.target_user.user_id, creature_dex_no=creature.dex_no if not self.show_variants else None, creature_id=creature.creature_id  if self.show_variants else None, environment_dex_no=self.environment.dex_no, time_of_day=self.time_of_day, is_mythical=True)
            creature_is_locked = total_mythical_catches_for_species == 0 if self.show_mythics else total_catches_for_creature_for_environment == 0

           # if creature is locked and is transcendant, skip it & don't display the icon
            if not (creature_is_locked and creature.default_rarity.name == TRANSCENDANT.name):
                dex_icon_img = self.build_dex_icon(creature=creature, total_catches=total_catches_for_creature_for_environment, total_mythical_catches=total_mythical_catches_for_species, creature_is_locked=creature_is_locked)
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
            first_caught_variant = get_tgommo_db_handler().get_first_caught_variant_for_creature(creature_dex_no=creature.dex_no, user_id=self.target_user.user_id, environment_dex_no=self.environment.dex_no, is_mythical=self.show_mythics)
            if first_caught_variant != 1:
                creature.variant_no = first_caught_variant
                creature.define_creature_images()

        dex_icon = EncyclopediaIconFactory(creature=creature, environment=self.environment, total_catches=total_catches, total_mythical_catches=total_mythical_catches, creature_is_locked=creature_is_locked, show_stats=self.is_verbose)
        return dex_icon.generate_dex_entry_image()

    def build_encyclopedia_dex_top_bar(self, encyclopedia_img: Image):
        top_bar_img = Image.open(ENCYCLOPEDIA_TOP_BAR_DEFAULT_IMAGE if not self.show_mythics else ENCYCLOPEDIA_TOP_BAR_SHINY_IMAGE)
        top_bar_img = Image.open(ENCYCLOPEDIA_TOP_BAR_SHINY_IMAGE if self.show_mythics else ENCYCLOPEDIA_TOP_BAR_NIGHT_IMAGE if self.time_of_day == NIGHT else ENCYCLOPEDIA_TOP_BAR_DAY_IMAGE if self.time_of_day == DAY  else ENCYCLOPEDIA_TOP_BAR_DEFAULT_IMAGE)

        top_bar_camera_img = Image.open(ENCYCLOPEDIA_TOP_BAR_CAMERA_ICON_IMAGE)
        top_bar_encounter_img = Image.open(ENCYCLOPEDIA_TOP_BAR_ENCOUNTER_ICON_IMAGE)

        encyclopedia_img.paste(top_bar_img, (0, 0), top_bar_img)
        encyclopedia_img.paste(top_bar_camera_img, (0, 0), top_bar_camera_img)
        encyclopedia_img.paste(top_bar_encounter_img, (0, 0), top_bar_encounter_img)

        return encyclopedia_img
    def build_encyclopedia_dex_bottom_bar(self, encyclopedia_img: Image):
        bottom_bar_img = Image.open(ENCYCLOPEDIA_BOTTOM_BAR_SHINY_IMAGE if self.show_mythics else ENCYCLOPEDIA_BOTTOM_BAR_NIGHT_IMAGE if self.time_of_day == NIGHT else ENCYCLOPEDIA_BOTTOM_BAR_DAY_IMAGE if self.time_of_day == DAY  else ENCYCLOPEDIA_BOTTOM_BAR_DEFAULT_IMAGE)
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
        text = f"Sketching Alley" if self.is_server_view else self.target_user.nickname
        font = resize_text_to_fit(text=text, draw=draw, font=name_font, max_width=475, min_font_size=10)
        pixel_location = (70, 535)
        draw.text(pixel_location, text= text, font=font, fill=FONT_COLOR_WHITE)

        if not self.is_server_view:
            text = f"@{self.target_user.discord_profile.name}"
            font = resize_text_to_fit(text=text, draw=draw, font=tag_font, max_width=260, min_font_size=10)
            pixel_location = (83, 593)
            draw.text(pixel_location, text= text, font=font, fill=FONT_COLOR_WHITE)

        # TOP BAR TEXT
        bar_font_color = FONT_COLOR_DARK_GRAY if self.show_mythics else FONT_COLOR_WHITE

        text = f"{'0' if self.unique_catches_for_user < 10 else ''} {self.unique_catches_for_user} / {'0' if self.unique_creatures_available_for_environment < 10 else ''} {self.unique_creatures_available_for_environment}"
        pixel_location = get_centered_text_position(text, bar_font, center_pixel_location=(858, 109))
        draw.text(pixel_location, text= text, font=bar_font, fill=bar_font_color)

        text = f"{self.total_user_catches}"
        pixel_location = get_centered_text_position(text, bar_font, center_pixel_location=(1082, 109))
        draw.text(pixel_location, text=text, font=bar_font, fill=bar_font_color)

        # BOTTOM BAR TEXT
        text = f"{self.environment.name}"
        font = resize_text_to_fit(text=text, draw=draw, font=bar_font, max_width=225, min_font_size=10)
        pixel_location = get_centered_text_position(text, font, center_pixel_location=(950, 630))
        draw.text(pixel_location, text=text, font=font, color=bar_font_color)

        return encyclopedia_img
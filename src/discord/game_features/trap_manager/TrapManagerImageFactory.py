import math

from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.trap_manager.TrapManagerCreatureCellImageFactory import TrapManagerCreatureCellImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class TrapManagerImageFactory(BaseImageFactory):
    def __init__(self, message_author, open_tab=TRAP_MANAGER_OPEN_TAB_SUMMARY):
        super().__init__(message_author=message_author, target_user=message_author)

        # Image Factory Properties
        self.open_tab = open_tab

        self.player_trap_link = get_tgommo_db_handler().get_player_trap_link_by_user_id(user_id=self.target_user.user_id)
        self.active_trap = self.player_trap_link.active_trap
        self.active_trap_rarity = self.active_trap.rarity.name

        # Captures Tab Properties
        # todo: grab these from db, add a flag for if the creature was remotely caught or not, and sort by most recent catch date first
        self.creatures_caught_by_trap = get_tgommo_db_handler().get_user_creatures_by_user_id(user_id=self.target_user.user_id)[1:]
        self.creature_icons = self.build_creature_cell_images()
        self.total_pages = math.ceil(len(self.creature_icons) / 32) if len(self.creature_icons) > 0 else 1

        # todo: remove
        self.page_num = 2

        self.load_relevant_info()

    def reload_image(self, target_user=None, player_trap_link=None, new_page_number=None, open_tab=None):
        self.load_relevant_info(target_user= target_user, player_trap_link=player_trap_link, new_page_number=new_page_number, open_tab=open_tab)
        return self.build_image()
    def load_relevant_info(self, target_user=None, player_trap_link=None, new_page_number=None, open_tab=None):
        self.target_user = target_user if target_user else self.target_user
        self.page_num = new_page_number if new_page_number else self.page_num
        self.open_tab = open_tab if open_tab else self.open_tab

        if player_trap_link:
            self.player_trap_link = player_trap_link
            self.active_trap = self.player_trap_link.active_trap
            self.active_trap_rarity = self.active_trap.rarity.name




    def build_image(self):
        trap_manager_image = Image.open(TRAP_MANAGER_BG_IMAGE)
        foreground_overlay_image = Image.open(f"{TRAP_MANAGER_FOREGROUND_TREE_BASE}_{self.active_trap_rarity}{IMAGE_FILE_EXTENSION}")
        corner_overlay_image = Image.open(TRAP_MANAGER_CORNER_OVERLAY_IMAGE)
        active_trap = self.active_trap.item_image

        # paste BG resources
        trap_manager_image.paste(foreground_overlay_image, (0, 0), foreground_overlay_image)

        # build the summary menus if the summary tab is open
        if self.open_tab == TRAP_MANAGER_OPEN_TAB_SUMMARY:
            open_menu_overlay_image = Image.open(TRAP_MANAGER_SUMMARY_OVERLAY_IMAGE)
            trap_manager_mode_image = Image.open(f"{TRAP_MANAGER_OVERLAY_SUMMARY_TRAP_MODE_BASE}_{self.player_trap_link.active_trap_mode}{IMAGE_FILE_EXTENSION}")

            trap_manager_image.paste(open_menu_overlay_image, (0, 0), open_menu_overlay_image)
            trap_manager_image.paste(trap_manager_mode_image, (0, 0), trap_manager_mode_image)
            trap_manager_image.paste(active_trap, get_centered_image_position(foreground_image=active_trap, background_image=trap_manager_image, center_pixel=(1041, 527)), active_trap)

            # add the battery section to the trap manager image
            trap_manager_image = self.build_summary_battery_section(trap_manager_image)

        # otherwise build the captures menu
        elif self.open_tab == TRAP_MANAGER_OPEN_TAB_CAPTURES:
            open_menu_overlay_image = Image.open(TRAP_MANAGER_CAPTURES_OVERLAY_IMAGE)
            trap_manager_image.paste(open_menu_overlay_image, (0, 0), open_menu_overlay_image)

            # add active arrows to the trap manager image if there are more pages of creatures to show
            if self.page_num > 1:
                left_active_arrow = Image.open(TRAP_MANAGER_CAPTURES_ACTIVE_ARROW_LEFT_IMAGE)
                trap_manager_image.paste(left_active_arrow, (0, 0), left_active_arrow)
            if self.page_num < self.total_pages:
                right_active_arrow = Image.open(TRAP_MANAGER_CAPTURES_ACTIVE_ARROW_RIGHT_IMAGE)
                trap_manager_image.paste(right_active_arrow, (0, 0), right_active_arrow)

            # build the captures creature menu and paste it onto the trap manager image
            trap_manager_image = self.build_captures_creature_menu(trap_manager_image)

        # paste FG resources
        trap_manager_image.paste(corner_overlay_image, (0,0), corner_overlay_image)
        return self.add_text_to_image(image = trap_manager_image)

    def build_summary_battery_section(self, base_image: Image):
        battery_bars_image = Image.open(TRAP_MANAGER_SUMMARY_BATTERY_BARS_IMAGE)
        battery_full_image = Image.open(TRAP_MANAGER_SUMMARY_BATTERY_FULLY_CHARGED_IMAGE)
        battery_icon_image = Image.open(TRAP_MANAGER_SUMMARY_BATTERY_ICON_IMAGE)

        battery_glow_icon_image = Image.open(TRAP_MANAGER_SUMMARY_BATTERY_GLOW_ICON_IMAGE)

        # if the player has max charges, draw the fully charged battery image
        if self.player_trap_link.player_trap_charges == self.player_trap_link.player_max_trap_charges:
            base_image.paste(battery_full_image, (0, 0), battery_full_image)

        # Draw battery bars cropped from right to left based on charge ratio
        ratio = (self.player_trap_link.player_trap_charges / self.player_trap_link.player_max_trap_charges) if self.player_trap_link.player_max_trap_charges > 0 else 0
        width_to_show = int(battery_bars_image.width * ratio)
        if width_to_show > 0:
            cropped_bars = battery_bars_image.crop((0, 0, width_to_show, battery_bars_image.height))
            base_image.paste(cropped_bars, (1377, 946), cropped_bars)

        # Draw battery icons based on the number of charges, with a maximum of 8 charges per icon
        full_batteries = self.player_trap_link.player_trap_charges // 8
        remainder = self.player_trap_link.player_trap_charges % 8
        max_battery_slots = math.ceil(self.player_trap_link.player_max_trap_charges / 8) if self.player_trap_link.player_max_trap_charges > 0 else 0
        icon_w, icon_h = battery_icon_image.size

        starting_pos = (1583, 898)
        for i in range(max_battery_slots):
            # use a normal battery icon by default
            current_battery_icon = battery_icon_image
            # if the player has a partial battery left, crop the icon to show the correct charge level
            if i == full_batteries and remainder > 0:
                crop_ratio = remainder / 8.0
                crop_h = max(1, int(icon_h * crop_ratio))
                y_start = icon_h - crop_h
                partial_icon = battery_icon_image.crop((0, y_start, icon_w, icon_h))

                paste_y = icon_h - crop_h
                full_battery_icon = battery_glow_icon_image.copy()
                full_battery_icon.paste(partial_icon, (0, paste_y), partial_icon)

                current_battery_icon = full_battery_icon
            # if the player has an entire battery slot missing, use a blank
            elif i > full_batteries:
                current_battery_icon = None

            base_image.paste(battery_glow_icon_image, starting_pos, battery_glow_icon_image)
            if current_battery_icon:
                base_image.paste(current_battery_icon, starting_pos, current_battery_icon)
            starting_pos = (starting_pos[0] + battery_icon_image.width, starting_pos[1])
        return base_image

    def build_captures_creature_menu(self, base_image: Image):
        creature_grid = self.build_grid(icons=self.creature_icons, grid_size=(1172, 631), icon_size=(142, 150), icons_per_page=32, icons_per_row=8, horizontal_padding=5, vertical_padding=10)
        base_image.paste(creature_grid, (68, 260), creature_grid)
        return base_image

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        if self.open_tab == TRAP_MANAGER_OPEN_TAB_SUMMARY:
            if self.player_trap_link.active_trap_mode == TRAP_MODE_SCHEDULED:
                # Add scheduled trap mode message to image
                font, wrapped_text = resize_text_to_fit_newline(text=TRAP_MODE_SCHEDULED_MESSAGE.format(self.player_trap_link.trap_scheduled_start_time, self.player_trap_link.trap_scheduled_mode_end_time), draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 19), max_width=432, min_font_size=12, allow_newlines=True, max_lines=2)
                draw.text((240, 412), f"{wrapped_text}", fill=FONT_COLOR_TRAP_MANAGER_OFF_GREEN, font=font)

            # add active trap name to image
            font = resize_text_to_fit(text=self.active_trap.item_name, draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 44), max_width=396, min_font_size=40)
            draw.text((844, 228), f"{self.active_trap.item_name}", fill=FONT_COLOR_WHITE, font=font)

            # add active trap description to image
            font, wrapped_text = resize_text_to_fit_newline(text=self.active_trap.item_description, draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 16), max_width=396, min_font_size=10, allow_newlines=True, max_lines=6)
            draw.text((844, 846), f"{wrapped_text}", fill=FONT_COLOR_TRAP_MANAGER_OFF_BROWN, font=font)

            # add total charges text to image
            charges_text = f"{self.player_trap_link.player_trap_charges}/{self.player_trap_link.player_max_trap_charges}"
            font = resize_text_to_fit(text=f"{charges_text}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 16), max_width=58, min_font_size=10)
            draw.text(get_centered_text_position(text=charges_text, font=font, center_pixel_location=(1544, 957)), f"{charges_text}", fill=FONT_COLOR_TRAP_MANAGER_OFF_BROWN, font=font)

        elif self.open_tab == TRAP_MANAGER_OPEN_TAB_CAPTURES:
            # add page number text to image
            page_text = f"Page {self.page_num}/{self.total_pages}"
            font = resize_text_to_fit(text=f"{page_text}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 22), max_width=100, min_font_size=10)
            draw.text(get_centered_text_position(text=page_text, font=font, center_pixel_location=(654, 954)), f"{page_text}", fill=FONT_COLOR_TRAP_MANAGER_OFF_BROWN, font=font)

            # ADD TEXT FOR AFK CATCH RESULTS
            # add xp text to image
            total_catch_text = f"{len(self.creatures_caught_by_trap)}"
            font = resize_text_to_fit(text=f"{total_catch_text}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 35), max_width=104, min_font_size=10)
            draw.text(get_centered_text_position(text=f"{total_catch_text}", font=font, center_pixel_location=(1496, 720)), f"{total_catch_text}", fill=FONT_COLOR_WHITE, font=font)

            # add xp text to image
            xp_text = sum(creature.xp_earned for creature in self.creatures_caught_by_trap)
            font = resize_text_to_fit(text=f"{xp_text}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 35), max_width=104, min_font_size=10)
            draw.text(get_centered_text_position(text=f"{xp_text}", font=font, center_pixel_location=(1496, 832)), f"{xp_text}", fill=FONT_COLOR_WHITE, font=font)

            # add gold text to image
            gold_text = sum(creature.gold_earned for creature in self.creatures_caught_by_trap)
            font = resize_text_to_fit(text=f"{gold_text}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 35), max_width=104, min_font_size=10)
            draw.text(get_centered_text_position(text=f"{gold_text}", font=font, center_pixel_location=(1496, 934)), f"{gold_text}", fill=FONT_COLOR_WHITE, font=font)

            # add rarity results text to image
            rarity_counts = {
                sum(1 for creature in self.creatures_caught_by_trap if creature.local_rarity.name == TGOMMO_RARITY_COMMON): (1800, 685),
                sum(1 for creature in self.creatures_caught_by_trap if creature.local_rarity.name == TGOMMO_RARITY_UNCOMMON): (1800, 735),
                sum(1 for creature in self.creatures_caught_by_trap if creature.local_rarity.name == TGOMMO_RARITY_RARE): (1800, 785),
                sum(1 for creature in self.creatures_caught_by_trap if creature.local_rarity.name == TGOMMO_RARITY_EPIC): (1800, 835),
                sum(1 for creature in self.creatures_caught_by_trap if creature.local_rarity.name == TGOMMO_RARITY_LEGENDARY): (1800, 885),
                sum(1 for creature in self.creatures_caught_by_trap if creature.local_rarity.name == TGOMMO_RARITY_MYTHICAL): (1800, 935),
                sum(1 for creature in self.creatures_caught_by_trap if creature.local_rarity.name == TGOMMO_RARITY_TRANSCENDANT): (1800, 985),
            }
            for count, position in rarity_counts.items():
                font = resize_text_to_fit(text=f"{count}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 35), max_width=100, min_font_size=10)
                draw.text(get_centered_text_position(text=f"{count}", font=font, center_pixel_location=position), f"{count}", fill=FONT_COLOR_WHITE, font=font)
        return image

    '''---- SUPPORT FUNCTIONS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def build_creature_cell_images(self):
        creature_icons = []
        for creature in self.creatures_caught_by_trap:
            creature_cell_image = TrapManagerCreatureCellImageFactory(creature=creature).generate_creature_cell_image()
            creature_icons.append(creature_cell_image)
        return creature_icons

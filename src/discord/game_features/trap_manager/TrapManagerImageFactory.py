import math

from src.commons.CommonFunctions import *
from src.discord.game_features.trap_manager.TrapManagerCreatureCellImageFactory import \
    TrapManagerCreatureCellImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class TrapManagerImageFactory(BaseImageFactory):
    def __init__(self, message_author, open_tab=TRAP_MANAGER_OPEN_TAB_SUMMARY):
        super().__init__(message_author=message_author, target_user=message_author)

        # Image Factory Variables
        self.open_tab = open_tab

        # todo: pull these from the database based on the player profile id
        (self.active_trap_rarity,
         self.active_trap_mode,
         self.player_trap_charges,
         self.player_trap_max_charges) = None, None, 18, 24

        self.load_relevant_info()

    def build_image(self):
        trap_manager_image = Image.open(TRAP_MANAGER_BG_IMAGE)
        foreground_overlay_image = Image.open(f"{TRAP_MANAGER_FOREGROUND_TREE_BASE}{self.active_trap_rarity}{IMAGE_FILE_EXTENSION}")
        trap_manager_image.paste(foreground_overlay_image, (0, 0), foreground_overlay_image)

        if self.open_tab == TRAP_MANAGER_OPEN_TAB_SUMMARY:
            open_menu_overlay_image = Image.open(TRAP_MANAGER_SUMMARY_OVERLAY_IMAGE)
            trap_manager_mode_image = Image.open(f"{TRAP_MANAGER_OVERLAY_SUMMARY_TRAP_MODE_BASE}_{self.active_trap_mode}{IMAGE_FILE_EXTENSION}")

            trap_manager_image.paste(open_menu_overlay_image, (0, 0), open_menu_overlay_image)
            trap_manager_image.paste(trap_manager_mode_image, (0, 0), trap_manager_mode_image)

            # add the battery section to the trap manager image
            trap_manager_image = self.build_summary_battery_section(trap_manager_image)
        else:
            if self.page_num > 1:
                left_active_arrow = Image.open(TRAP_MANAGER_CAPTURES_ACTIVE_ARROW_LEFT_IMAGE)
                trap_manager_image.paste(left_active_arrow, (0, 0), left_active_arrow)
            if self.page_num < self.total_pages:
                right_active_arrow = Image.open(TRAP_MANAGER_CAPTURES_ACTIVE_ARROW_RIGHT_IMAGE)
                trap_manager_image.paste(right_active_arrow, (0, 0), right_active_arrow)
            trap_manager_image = self.build_captures_creature_menu(trap_manager_image)
        return trap_manager_image

    def build_summary_battery_section(self, base_image: Image):
        battery_bars_image = Image.open(TRAP_MANAGER_SUMMARY_BATTERY_BARS_IMAGE)
        battery_full_image = Image.open(TRAP_MANAGER_SUMMARY_BATTERY_FULLY_CHARGED_IMAGE)
        battery_icon_image = Image.open(TRAP_MANAGER_SUMMARY_BATTERY_ICON_IMAGE)

        if self.player_trap_charges == self.player_trap_max_charges:
            base_image.paste(battery_full_image, (0, 0), battery_full_image)

        # Draw battery bars cropped from right to left based on charge ratio
        ratio = (self.player_trap_charges / self.player_trap_max_charges) if self.player_trap_max_charges > 0 else 0
        width_to_show = int(battery_bars_image.width * ratio)
        if width_to_show > 0:
            cropped_bars = battery_bars_image.crop((0, 0, width_to_show, battery_bars_image.height))
            base_image.paste(cropped_bars, (1377, 946), cropped_bars)

        # Place battery icons: one full icon per 8 charges, plus a partial cropped icon for remainder
        full_batteries = self.player_trap_charges // 8
        remainder = self.player_trap_charges % 8
        max_battery_slots = math.ceil(self.player_trap_max_charges / 8) if self.player_trap_max_charges > 0 else 0

        start_x, start_y = 1590, 905
        icon_w, icon_h = battery_icon_image.size

        for i in range(full_batteries):
            x = start_x + (i * 50)
            base_image.paste(battery_icon_image, (x, start_y), battery_icon_image)

        # partial battery icon for remainder
        if remainder > 0 and full_batteries < max_battery_slots:
            crop_ratio = remainder / 8.0
            crop_h = max(1, int(icon_h * crop_ratio))

            # crop the top portion of the icon
            y_start = icon_h - crop_h
            partial_icon = battery_icon_image.crop((0, y_start, icon_w, icon_h))

            x = start_x + (full_batteries * 50)
            paste_y = start_y + (icon_h - crop_h)
            base_image.paste(partial_icon, (x, paste_y), partial_icon)

        return base_image

    def build_captures_creature_menu(self, base_image: Image):
        creature_icons = []

        # todo: grab these from db, add a flag for if the creature was remotely caught or not, and sort by most recent catch date first
        creatures_caught_by_trap = []

        for creature in creatures_caught_by_trap:
            creature_cell_image = TrapManagerCreatureCellImageFactory(creature=creature).generate_creature_cell_image()
            creature_icons.append(creature_cell_image)
        creature_grid = self.build_grid(icons=creature_icons, grid_size=(1172, 631), icon_size=(142, 150), icons_per_page=32, icons_per_row=8, horizontal_padding=5, vertical_padding=10)

        return base_image.paste(creature_grid, (68, 260), creature_grid)

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)
        return
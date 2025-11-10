from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import convert_to_png, center_text_on_pixel
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_inventory.CreatureInventoryIconImageFactory import \
    CreatureInventoryIconImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class CreatureInventoryImageFactory:
    def __init__(self, user, show_mythics_only= False, show_nicknames_only= False, show_favorites_only= False):
        self.user = user

        self.show_mythics_only = show_mythics_only
        self.show_nicknames_only = show_nicknames_only
        self.show_favorites_only = show_favorites_only

        self.caught_creatures = []
        self.caught_creatures_icons = []
        self.selected_creature = None
        self.order_type = CAUGHT_DATE_ORDER

        self.current_box_num = 1
        self.total_unlocked_box_num = 8
        self.total_box_num = 15

        self.load_relevant_info()

        self.is_release_confirmation_active = False


    def load_relevant_info(self):
        self.caught_creatures = get_tgommo_db_handler().get_creature_collection_by_user(self.user.id, convert_to_object=True,)
        self.caught_creatures_icons = self.get_creature_icons(self.caught_creatures)

    def build_creature_inventory_page_image(self, new_box_number = None, is_release_confirmation_active = None, show_mythics_only= False, show_nicknames_only= False, show_favorites_only= False, order_type= None):
        #define init settings
        self.show_mythics_only = show_mythics_only
        self.show_nicknames_only = show_nicknames_only
        self.show_favorites_only = show_favorites_only
        self.order_type = order_type if order_type else self.order_type
        self.current_box_num = new_box_number if new_box_number else self.current_box_num
        self.is_release_confirmation_active = is_release_confirmation_active if is_release_confirmation_active is not None else self.is_release_confirmation_active

        # construct base layers, start with environment bg
        background_img = Image.open(CREATURE_INVENTORY_BG_RELEASE_IMAGE if self.is_release_confirmation_active else CREATURE_INVENTORY_BG_IMAGE)
        corner_overlay_img = Image.open(CREATURE_INVENTORY_CORNER_OVERLAY_IMAGE)
        menu_bg_img = Image.open(CREATURE_INVENTORY_MENU_RELEASE_OVERLAY_IMAGE if self.is_release_confirmation_active else CREATURE_INVENTORY_MENU_OVERLAY_IMAGE)

        # place foreground_items
        background_img.paste(menu_bg_img, (0, 0), menu_bg_img)
        background_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)

        # place box icons
        background_img = self.place_box_icons_on_image(background_img)

        # place icon grid
        if not self.is_release_confirmation_active:
            icons = self.get_filtered_creatures(self.caught_creatures, self.caught_creatures_icons) if not self.is_release_confirmation_active else self.get_creature_icons(self.get_creatures_for_release())
            icons_grid = self.build_creature_inventory_icons_grid(creature_icons= icons)
            background_img.paste(icons_grid, (160, 260), icons_grid)

        background_img = self.add_text_to_image(background_img)
        return background_img

    def place_box_icons_on_image(self, image: Image.Image):
        box_icon_img = Image.open(CREATURE_INVENTORY_BOX_ICON).resize((100, 100))
        selected_box_icon_img = Image.open(CREATURE_INVENTORY_BOX_ICON_SELECTED).resize((100, 100))
        locked_box_icon_img = Image.open(CREATURE_INVENTORY_BOX_ICON_LOCKED).resize((100, 100))

        current_coordinates = (200, 127)
        x_offset = 100

        for box_num in range(1, self.total_box_num + 1):
            if box_num > self.total_unlocked_box_num:
                current_box_icon = locked_box_icon_img
            else:
                current_box_icon = selected_box_icon_img if box_num == self.current_box_num else box_icon_img
            image.paste(current_box_icon, current_coordinates, current_box_icon)
            current_coordinates = (current_coordinates[0] + x_offset, current_coordinates[1])

        return image

    def build_creature_inventory_icons_grid(self, creature_icons):
        grid_canvas = Image.new('RGBA', (1600, 720), (0, 0, 0, 0))

        icon_width, icon_height = 80, 144
        icons_per_row = 20

        # Calculate padding
        horizontal_padding = 0
        vertical_padding = 0

        # Define parameters for which icons will appear on page
        icons_per_page = 100
        starting_index = (self.current_box_num - 1) * icons_per_page
        ending_index = min(starting_index + icons_per_page, len(creature_icons))

        row, col = 0, 0
        for i in range(starting_index, ending_index):
            creature_icon = creature_icons[i]

            # Calculate position
            x = col * (icon_width + horizontal_padding if i != 0 else 0)
            y = row * (icon_height + vertical_padding if i != 0 else 0)

            # Paste icon onto canvas
            grid_canvas.paste(creature_icon, (int(x), int(y)), creature_icon)

            # Move to next position
            col += 1
            if col >= icons_per_row:
                col = 0
                row += 1

        return grid_canvas

    def get_creature_icons(self, creatures):
        imgs = []
        for creature in creatures:
            creature_icon = CreatureInventoryIconImageFactory(creature=creature)
            creature_icon_img = creature_icon.generate_inventory_icon_image()

            imgs.append(creature_icon_img)
        return imgs


    # return list of caught creatures to display based on filters
    def get_filtered_creatures(self, creatures, creature_icons):
        creatures, creature_icons = self.order_creatures_based_on_filter_type(creatures, creature_icons)
        filtered_creature_icons = []

        for i, creature in enumerate(creatures):
            if self.show_mythics_only and creature.rarity.name != TGOMMO_RARITY_MYTHICAL:
                continue
            if self.show_nicknames_only and creature.nickname == '':
                continue
            if self.show_favorites_only and not creature.is_favorite:
                continue
            filtered_creature_icons.append(creature_icons[i])
        return filtered_creature_icons


    def order_creatures_based_on_filter_type(self, creatures, creature_icons):
        paired_data = list(zip(creatures, creature_icons))

        if self.order_type == DEX_NO_ORDER:
            sorted_pairs = sorted(paired_data, key=lambda pair: pair[0].dex_no, reverse=False)
        elif self.order_type == ALPHABETICAL_ORDER:
            sorted_pairs = sorted(paired_data, key=lambda pair: pair[0].name.lower())
        else:
            sorted_pairs = sorted(paired_data, key=lambda pair: pair[0].caught_date, reverse=True)

        creatures, creature_icons = zip(*sorted_pairs) if sorted_pairs else ([], [])
        creatures = list(creatures)
        creature_icons = list(creature_icons)
        return creatures, creature_icons

    def add_text_to_image(self, image: Image.Image):
        draw = ImageDraw.Draw(image)
        default_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 36)

        box_num_text = f"BOX {self.current_box_num}"
        pixel_location = center_text_on_pixel(text= box_num_text, font=default_font, center_pixel_location=(960, 90))
        draw.text(pixel_location, text=box_num_text, font=default_font, fill=(200, 255, 185))

        return image


    def get_creatures_for_release(self):
        creatures_for_release = []
        for creature in self.caught_creatures:
            if creature.creature_id in self.user.selected_creatures_for_release:
                creatures_for_release.append(creature)
        return creatures_for_release
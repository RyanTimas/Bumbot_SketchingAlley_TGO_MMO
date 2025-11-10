from PIL import Image

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_inventory.CreatureInventoryIconImageFactory import \
    CreatureInventoryIconImageFactory
from src.resources.constants.file_paths import *


class CreatureInventoryImageFactory:
    def __init__(self, user, show_mythics_only= False, show_nicknames_only= False):
        self.user = user

        self.show_mythics_only = show_mythics_only
        self.show_nicknames_only = show_nicknames_only

        self.caught_creatures = []
        self.caught_creatures_icons = []
        self.selected_creature = None


        self.current_box_num = 1
        self.total_box_num = 1

        self.load_relevant_info()

        self.is_release_confirmation_active = False

    def load_relevant_info(self):
        self.caught_creatures = get_tgommo_db_handler().get_creature_collection_by_user(self.user.id, convert_to_object=True,)
        self.caught_creatures_icons = self.get_creature_icons(self.caught_creatures)

    def build_creature_inventory_page_image(self, new_box_number = None, is_release_confirmation_active = None):
        self.current_box_num = new_box_number if new_box_number else self.current_box_num
        self.is_release_confirmation_active = is_release_confirmation_active if is_release_confirmation_active is not None else self.is_release_confirmation_active

        # construct base layers, start with environment bg
        background_img = Image.open(CREATURE_INVENTORY_BG_RELEASE_IMAGE if self.is_release_confirmation_active else CREATURE_INVENTORY_BG_IMAGE)
        corner_overlay_img = Image.open(CREATURE_INVENTORY_CORNER_OVERLAY_IMAGE)
        menu_bg_img = Image.open(CREATURE_INVENTORY_MENU_RELEASE_OVERLAY_IMAGE if self.is_release_confirmation_active else CREATURE_INVENTORY_MENU_OVERLAY_IMAGE)

        # place foreground_items
        background_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)
        background_img.paste(menu_bg_img, (0, 0), menu_bg_img)

        # place box icons
        background_img = self.place_box_icons_on_image(background_img)

        # place icon grid
        if not self.is_release_confirmation_active:
            icons = self.caught_creatures_icons if not self.is_release_confirmation_active else self.get_creature_icons(self.get_creatures_for_release())
            icons_grid = self.build_creature_inventory_icons_grid(creature_icons= icons)
            background_img.paste(icons_grid, (160, 260), icons_grid)

        return background_img


    def place_box_icons_on_image(self, image: Image.Image):
        box_icon_img = Image.open(CREATURE_INVENTORY_BOX_ICON).resize((100, 100))
        selected_box_icon_img = Image.open(CREATURE_INVENTORY_BOX_ICON_SELECTED).resize((100, 100))

        current_coordinates = (200, 127)
        x_offset = 100

        for box_num in range(1, self.total_box_num + 1):
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
        ending_index = min(starting_index + icons_per_page, len(self.caught_creatures_icons))

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

            # Stop if we run out of space
            if row * icon_height + icon_height > 500:
                break

        return grid_canvas

    def get_creature_icons(self, creatures):
        imgs = []
        for creature in creatures:
            creature_icon = CreatureInventoryIconImageFactory(creature=creature)
            creature_icon_img = creature_icon.generate_inventory_icon_image()

            # imgs.append(convert_to_png(creature_icon_img, f'creature_icon_{creature.img_root}.png'))
            imgs.append(creature_icon_img)
        return imgs

    def get_creatures_for_release(self):
        creatures_for_release = []
        for creature in self.caught_creatures:
            if creature.creature_id in self.user.selected_creatures_for_release:
                creatures_for_release.append(creature)
        return creatures_for_release
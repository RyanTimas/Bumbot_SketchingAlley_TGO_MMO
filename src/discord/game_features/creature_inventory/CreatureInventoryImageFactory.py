from PIL import Image, ImageDraw, ImageFont, ImageFilter
from sqlalchemy.sql.functions import count

from src.commons.CommonFunctions import convert_to_png, center_text_on_pixel
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.creature_inventory.CreatureInventoryIconImageFactory import \
    CreatureInventoryIconImageFactory
from src.discord.game_features.creature_inventory.CreatureInventoryReleaseResultItemImageFactory import \
    CreatureInventoryReleaseResultItemImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class CreatureInventoryImageFactory:
    def __init__(self, user, show_mythics_only= False, show_nicknames_only= False, show_favorites_only= False):
        self.user = user

        # define filter & order settings
        self.order_type = CAUGHT_DATE_ORDER
        self.is_ascending_order = False

        self.show_mythics_only = show_mythics_only
        self.show_nicknames_only = show_nicknames_only
        self.show_favorites_only = show_favorites_only
        self.is_exclusive_mode = False


        # define creature management items
        self.caught_creatures = get_tgommo_db_handler().get_creature_collection_by_user(self.user.id, convert_to_object=True,)
        self.caught_creatures_icons = self.build_creature_icons()
        self.caught_creatures, self.caught_creatures_icons = self.order_creatures_based_on_filter_type()
        self.filtered_creatures, self.filtered_creature_icons = self.filter_user_creatures()

        # define parameters for which icons will appear on page
        self.starting_index = 0
        self.ending_index = min(0, len(self.filtered_creatures))
        self.current_box_num = 1
        self.total_unlocked_box_num = 8
        self.total_box_num = 15

        # define image mode
        self.image_mode = CREATURE_INVENTORY_MODE_DEFAULT
        self.creature_ids_to_update = []


    # CONSTRUCT IMAGE FUNCTIONS
    def get_creature_inventory_page_image(self, new_box_number = None, show_mythics_only= False, show_nicknames_only= False, show_favorites_only= False, order_type= None, image_mode= None, creature_ids_to_update= None, refresh_creatures= False, is_ascending_order= False, is_exclusive_mode= False):
        self.refresh_creature_inventory_image(new_box_number=new_box_number, show_mythics_only=show_mythics_only, show_nicknames_only=show_nicknames_only, show_favorites_only=show_favorites_only, order_type=order_type, image_mode=image_mode, creature_ids_to_update=creature_ids_to_update, refresh_creatures=refresh_creatures, is_ascending_order=is_ascending_order, is_exclusive_mode=is_exclusive_mode)
        return self.build_creature_inventory_page_image()

    def refresh_creature_inventory_image(self, new_box_number, show_mythics_only= False, show_nicknames_only= False, show_favorites_only= False, order_type= None, image_mode= None, creature_ids_to_update= None, refresh_creatures= False, is_ascending_order= False, is_exclusive_mode= False):
        # define filter & order settings
        self.order_type = order_type if order_type else self.order_type
        self.is_ascending_order = is_ascending_order

        self.show_mythics_only = show_mythics_only
        self.show_nicknames_only = show_nicknames_only
        self.show_favorites_only = show_favorites_only
        self.is_exclusive_mode = is_exclusive_mode

        # define creature management items
        if refresh_creatures:
            self.caught_creatures = get_tgommo_db_handler().get_creature_collection_by_user(self.user.id, convert_to_object=True,)
            self.caught_creatures_icons = self.build_creature_icons()
        self.caught_creatures, self.caught_creatures_icons = self.order_creatures_based_on_filter_type()
        self.filtered_creatures, self.filtered_creature_icons = self.filter_user_creatures()

        # define parameters for which icons will appear on page
        self.current_box_num = new_box_number if new_box_number else self.current_box_num
        self.starting_index = (self.current_box_num - 1) * 100
        self.ending_index = min(self.starting_index + 100, len(self.filtered_creature_icons))

        # define image mode
        self.image_mode = image_mode if image_mode else CREATURE_INVENTORY_MODE_DEFAULT
        self.creature_ids_to_update = creature_ids_to_update if creature_ids_to_update else []

    def build_creature_inventory_page_image(self):
        mode_image_paths = {
            CREATURE_INVENTORY_MODE_DEFAULT: (CREATURE_INVENTORY_BG_IMAGE, CREATURE_INVENTORY_MENU_OVERLAY_IMAGE),
            CREATURE_INVENTORY_MODE_RELEASE: (CREATURE_INVENTORY_BG_RELEASE_IMAGE, CREATURE_INVENTORY_MENU_RELEASE_OVERLAY_IMAGE),
            CREATURE_INVENTORY_MODE_FAVORITE: (CREATURE_INVENTORY_BG_RELEASE_IMAGE, CREATURE_INVENTORY_MENU_FAVORITE_OVERLAY_IMAGE)
        }

        # construct base layers, start with environment bg
        background_img = Image.open(mode_image_paths[self.image_mode][0])
        corner_overlay_img = Image.open(CREATURE_INVENTORY_CORNER_OVERLAY_IMAGE)
        menu_bg_img = Image.open(mode_image_paths[self.image_mode][1])

        # place foreground_items
        background_img.paste(menu_bg_img, (0, 0), menu_bg_img)

        # place creature icons grid
        icons_grid = self.build_creature_inventory_icons_grid()
        background_img.paste(icons_grid, (160, 260), icons_grid)

        # place box icons
        if self.image_mode == CREATURE_INVENTORY_MODE_DEFAULT:
            background_img = self.place_box_icons_on_image(background_img)

        # add text to image
        if self.image_mode == CREATURE_INVENTORY_MODE_DEFAULT:
            background_img = self.add_text_to_image(background_img)

        background_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)
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

    def build_creature_inventory_icons_grid(self):
        grid_canvas = Image.new('RGBA', (1600, 720), (0, 0, 0, 0))

        icon_width, icon_height = 80, 144
        icons_per_row = 20

        # Calculate padding
        horizontal_padding = 0
        vertical_padding = 0
        row, col = 0, 0

        for i in range(self.starting_index, self.ending_index):
            creature_icon = self.filtered_creature_icons[i]

            if self.image_mode == CREATURE_INVENTORY_MODE_RELEASE:
                icon_is_invisible = str(self.caught_creatures[i].catch_id) not in self.creature_ids_to_update
                creature_icon.putalpha(0 if icon_is_invisible else 255)

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
    def build_creature_icons(self):
        imgs = []
        for creature in self.caught_creatures:
            creature_icon = CreatureInventoryIconImageFactory(creature=creature)
            creature_icon_img = creature_icon.generate_inventory_icon_image()

            imgs.append(creature_icon_img)
        return imgs


    def add_text_to_image(self, image: Image.Image):
        draw = ImageDraw.Draw(image)
        # add box number text to image
        default_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 58)

        box_num_text = f"BOX {self.current_box_num}"
        pixel_location = center_text_on_pixel(text=box_num_text, font=default_font, center_pixel_location=(960, 90))
        draw.text(pixel_location, text=box_num_text, font=default_font, fill=(200, 255, 185))

        return image


    # SUPPORT FUNCTIONS
    # return list of caught creatures to display based on filters
    def filter_user_creatures(self):
        filtered_creatures = []
        filtered_creature_icons = []

        for i, creature in enumerate(self.caught_creatures):
            if self.show_mythics_only and (creature.rarity.name != TGOMMO_RARITY_MYTHICAL if not self.is_exclusive_mode else creature.rarity.name == TGOMMO_RARITY_MYTHICAL):
                continue
            if self.show_nicknames_only and (creature.nickname == '' if not self.is_exclusive_mode else creature.nickname != ''):
                continue
            if self.show_favorites_only and not (creature.is_favorite if not self.is_exclusive_mode else not creature.is_favorite):
                continue
            filtered_creatures.append(creature)
            filtered_creature_icons.append(self.caught_creatures_icons[i])

        return filtered_creatures, filtered_creature_icons

    def order_creatures_based_on_filter_type(self):
        paired_data = list(zip(self.caught_creatures, self.caught_creatures_icons))

        if self.order_type == DEX_NO_ORDER:
            sorted_pairs = sorted(paired_data, key=lambda pair: pair[0].dex_no, reverse=self.is_ascending_order)
        elif self.order_type == ALPHABETICAL_ORDER:
            sorted_pairs = sorted(paired_data, key=lambda pair: pair[0].name.lower(), reverse=self.is_ascending_order)
        else:
            sorted_pairs = sorted(paired_data, key=lambda pair: pair[0].caught_date, reverse=not self.is_ascending_order)

        creatures, creature_icons = zip(*sorted_pairs) if sorted_pairs else ([], [])
        creatures = list(creatures)
        creature_icons = list(creature_icons)
        return creatures, creature_icons


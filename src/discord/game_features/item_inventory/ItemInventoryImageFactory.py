from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, add_border_to_image, get_centered_image_position
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.item_inventory.ItemInventoryIconImageFactory import ItemInventoryIconImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE, ITEM_INVENTORY_EXCLUDED_ITEM_TYPES, ITEM_INVENTORY_TABS
from src.resources.constants.file_paths import *


class ItemInventoryImageFactory(BaseImageFactory):
    def __init__(self, message_author, target_user):
        super().__init__(message_author=message_author, target_user=target_user)
        self.active_tab = next(iter(ITEM_INVENTORY_TABS.keys())) # Set the first tab as the default active tab

        self.user_items = [item for item in get_tgommo_db_handler().get_inventory_item_collection_by_user_id(user_id=self.target_user.user_id, convert_to_object=True) if item.item_quantity > 0 and item.item_type not in ITEM_INVENTORY_EXCLUDED_ITEM_TYPES]
        self.active_items = [item for item in self.user_items if item.item_type in  ITEM_INVENTORY_TABS.get(self.active_tab).get("item_types")]

        self.user_item_icons = self.build_item_icons()

        self.starting_index = 0
        self.ending_index = len(self.user_item_icons)


    def reload_image(self, target_user= None, new_page_number = None, active_tab=None):
        self.load_relevant_info(target_user=target_user, new_page_number=new_page_number, active_tab=active_tab)
        return self.build_image()

    def load_relevant_info(self, target_user= None, new_page_number = None, active_tab=None):
        super().load_relevant_info(target_user=target_user, new_page_number=new_page_number)
        if active_tab:
            self.active_tab = active_tab if active_tab else self.active_tab
            self.active_items = [item for item in self.user_items if item.item_type in ITEM_INVENTORY_TABS.get(self.active_tab).get("item_types")]

        data_changed = any(param is not None for param in [target_user])
        if data_changed:
            self.user_items = [item for item in get_tgommo_db_handler().get_inventory_item_collection_by_user_id(user_id=self.target_user.user_id, convert_to_object=True) if item.item_quantity > 0 and item.item_type not in ITEM_INVENTORY_EXCLUDED_ITEM_TYPES]
        self.user_item_icons = self.build_item_icons()

    def build_image(self):
        item_inventory_image = Image.open(ITEM_INVENTORY_BG_IMAGE)
        item_inventory_overlay = Image.open(ITEM_INVENTORY_CORNER_OVERLAY_IMAGE)

        active_item_icons = [self.user_item_icons[i] for i in  [i for i, item in enumerate(self.user_items) if item.item_id in {item.item_id for item in self.active_items}]]
        item_grid_img = self.build_grid(icons=active_item_icons, grid_size=(1512, 700), icons_per_page=20, icon_size=(500, 70), icons_per_row=3, horizontal_padding=6, vertical_padding=3)

        item_inventory_image.paste(item_grid_img, (216, 270), item_grid_img)
        item_inventory_image.paste(item_inventory_overlay, (0, 0), item_inventory_overlay)

        inventory_categories_grid, inventory_categories_grid_position = self.get_inventory_categories_grid(image=item_inventory_image)
        item_inventory_image.paste(inventory_categories_grid, inventory_categories_grid_position, inventory_categories_grid)

        return self.add_text_to_image(image=item_inventory_image)

    def build_item_icons(self):
        imgs = []
        for item in self.user_items:
            item_icon = ItemInventoryIconImageFactory(item=item)
            item_icon_img = item_icon.generate_inventory_icon_image()

            imgs.append(item_icon_img)
        return imgs

    def add_text_to_image(self, image: Image):
        return self.place_username_on_image(item_inventory_img=image)

    def place_username_on_image(self, item_inventory_img: Image):
        draw = ImageDraw.Draw(item_inventory_img)

        font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 75)
        font = resize_text_to_fit(text=self.target_user.nickname, draw=draw, font=font, max_width=300, min_font_size=10)

        # Get text dimensions
        text_bbox = draw.textbbox((0, 0), self.target_user.nickname, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Create a separate image for the text with border
        text_img = Image.new('RGBA', (text_width + 8, text_height + 8), (0, 0, 0, 0))
        x_offset, y_offset = 11, 10
        border_size = 4
        username_font_image = add_border_to_image(base_image=text_img, text=self.target_user.nickname, font=font, border_size=border_size, border_color=(216, 180, 87), font_color=FONT_COLOR_WHITE)

        # Paste the text image onto the profile image
        item_inventory_img.paste(username_font_image, (x_offset - border_size, y_offset - border_size), username_font_image)

        # draw.text((11, 10), self.player.nickname, font=font, fill=FONT_COLOR_WHITE)

        return item_inventory_img

    def get_inventory_categories_grid(self, image: Image):
        icons = []

        for i in range(len(ITEM_INVENTORY_TABS)):
            icon_key = list(ITEM_INVENTORY_TABS.keys())[i]
            icon_info = ITEM_INVENTORY_TABS[icon_key]
            icon_image = Image.open(icon_info.get("icon"))

            # reduce opacity to 35%
            if icon_key != self.active_tab:
                r, g, b, a = icon_image.split()
                a = a.point(lambda p: int(p * 0.65))
                icon_image.putalpha(a)
            icons.append(icon_image)

        icon_grid_max_width = 1414
        icon_dimensions = 125
        icon_grid_padding = max(0, (icon_grid_max_width - len(icons) * icon_dimensions) // (len(icons)))

        item_icons_grid = self.build_grid(icons=icons, grid_size=(icon_grid_max_width, 114), icons_per_page=20, icon_size=(icon_dimensions, icon_dimensions), icons_per_row=15, horizontal_padding=icon_grid_padding, vertical_padding=3)
        centered_image_position_x, centered_image_position_y = get_centered_image_position(foreground_image=item_icons_grid, background_image=image)
        return item_icons_grid, (centered_image_position_x, 116)

    def refresh_active_items(self):
        self.active_items = [item for item in self.user_items if item.item_type in ITEM_INVENTORY_TABS.get(self.active_tab).get("item_types")]

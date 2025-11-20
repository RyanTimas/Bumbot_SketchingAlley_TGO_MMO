from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, add_border_to_image
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.item_inventory.ItemInventoryIconImageFactory import ItemInventoryIconImageFactory
from src.discord.objects.TGOPlayerItem import TGOPlayerItem
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE
from src.resources.constants.file_paths import *


class ItemInventoryImageFactory:
    def __init__(self, user,):
        self.user = user

        self.user_items = get_tgommo_db_handler().get_item_collection_by_user_id(user_id=self.user.user_id, convert_to_object=True)
        self.user_item_icons = self.build_item_icons()

        self.starting_index = 0
        self.ending_index = len(self.user_item_icons)

    def generate_item_inventory_image(self, user = None):
        self.refresh_item_inventory_parameters(user=user)
        return self.build_item_inventory_page_image()

    def refresh_item_inventory_parameters(self, user):
        self.user = user is not None and user or self.user
        self.user_items = get_tgommo_db_handler().get_item_collection_by_user_id(user_id=self.user.user_id, convert_to_object=True)
        self.user_item_icons = self.build_item_icons()

    def build_item_inventory_page_image(self):
        item_inventory_image = Image.open(ITEM_INVENTORY_BG_IMAGE)
        item_inventory_overlay = Image.open(ITEM_INVENTORY_CORNER_OVERLAY_IMAGE)

        item_grid_img = self.build_items_inventory_icons_grid()
        item_inventory_image.paste(item_grid_img, (216, 270), item_grid_img)
        item_inventory_image.paste(item_inventory_overlay, (0, 0), item_inventory_overlay)

        return self.add_text_to_image(image=item_inventory_image)


    def build_items_inventory_icons_grid(self):
        grid_canvas = Image.new('RGBA', (1512, 700), (0, 0, 0, 0))

        icon_width, icon_height = 500, 70
        icons_per_row = 3

        # Calculate padding
        horizontal_padding = 6
        vertical_padding = 3
        row, col = 0, 0

        for i in range(self.starting_index, self.ending_index):
            creature_icon = self.user_item_icons[i]

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
    def build_item_icons(self):
        imgs = []
        for item in self.user_items:
            item_icon = ItemInventoryIconImageFactory(item=item)
            item_icon_img = item_icon.generate_inventory_icon_image()

            imgs.append(item_icon_img)
        return imgs


    def add_text_to_image(self, image: Image.Image):
        return self.place_username_on_image(item_inventory_img=image)

    def place_username_on_image(self, item_inventory_img: Image.Image):
        draw = ImageDraw.Draw(item_inventory_img)

        font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 75)
        font = resize_text_to_fit(text=self.user.nickname, draw=draw, font=font, max_width=300, min_font_size=10)

        # Get text dimensions
        text_bbox = draw.textbbox((0, 0), self.user.nickname, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Create a separate image for the text with border
        text_img = Image.new('RGBA', (text_width + 8, text_height + 8), (0, 0, 0, 0))
        x_offset, y_offset = 11, 10
        border_size = 4
        username_font_image = add_border_to_image(base_image=text_img, text=self.user.nickname, font=font, border_size=border_size, border_color=(216, 180, 87), font_color=FONT_COLOR_WHITE)

        # Paste the text image onto the profile image
        item_inventory_img.paste(username_font_image, (x_offset - border_size, y_offset - border_size), username_font_image)

        # draw.text((11, 10), self.player.nickname, font=font, fill=FONT_COLOR_WHITE)

        return item_inventory_img
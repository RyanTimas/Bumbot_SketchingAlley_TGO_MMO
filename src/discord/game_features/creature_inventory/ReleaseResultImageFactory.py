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


class ReleaseResultImageFactory:
    def __init__(self, user, show_mythics_only= False, show_nicknames_only= False, show_favorites_only= False):
        self.user = user

        self.creature_ids_to_update = []

        self.currency = 0
        self.earned_items = []
        self.count_released = 0


    # CONSTRUCT IMAGE FUNCTIONS
    def get_creature_inventory_page_image(self, creature_ids_to_update= None, currency= 0, earned_items= None, count_released= 0):
        self.refresh_creature_inventory_image(creature_ids_to_update=creature_ids_to_update, currency=currency, earned_items=earned_items, count_released=count_released)
        return self.build_creature_inventory_page_image()

    def refresh_creature_inventory_image(self, creature_ids_to_update= None, currency= 0, earned_items= None, count_released= 0):
        self.creature_ids_to_update = creature_ids_to_update if creature_ids_to_update else []

        self.currency = currency
        self.earned_items = earned_items
        self.count_released = count_released

    def build_creature_inventory_page_image(self):
        # construct base layers, start with environment bg
        background_img = Image.open(CREATURE_INVENTORY_BG_IMAGE).filter(ImageFilter.GaussianBlur(radius=8))
        release_results_bg_img = Image.open(CREATURE_INVENTORY_RELEASE_SUMMARY_BG_IMAGE)
        items_grid = self.build_release_summary_items_grid()

        background_img.paste(release_results_bg_img, (0, 0), release_results_bg_img)
        background_img.paste(items_grid, (130, 360), items_grid)

        background_img = self.add_text_to_image(background_img)
        return background_img


    def build_release_summary_items_grid(self):
        grid_canvas = Image.new('RGBA', (1658, 634), (0, 0, 0, 0))

        icon_width, icon_height = 826, 126
        icons_per_row = 2

        # Calculate padding
        horizontal_padding = 1
        vertical_padding = 1
        row, col = 0, 0

        for i, item_icon in enumerate(self.build_items_icons()):
            # Calculate position
            x = col * (icon_width + horizontal_padding if i != 0 else 0)
            y = row * (icon_height + vertical_padding if i != 0 else 0)

            # Paste icon onto canvas
            grid_canvas.paste(item_icon, (int(x), int(y)), item_icon)

            # Move to next position
            col += 1
            if col >= icons_per_row:
                col = 0
                row += 1


        return grid_canvas
    def build_items_icons(self):
        imgs = []
        for item in self.earned_items:
            item_icon = CreatureInventoryReleaseResultItemImageFactory(item=item[0], count=item[1])
            item_img = item_icon.generate_release_result_item_icon_image()

            imgs.append(item_img)
        return imgs


    def add_text_to_image(self, image: Image.Image):
        draw = ImageDraw.Draw(image)
        navy_blue_color = (38, 36, 109)

        name_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 28)

        # add username footer
        name_text = f"{get_tgommo_db_handler().get_user_profile_by_user_id(user_id=self.user.id, convert_to_object=True).nickname}'s Release Summary"
        pixel_location = center_text_on_pixel(text=name_text, font=name_font, center_pixel_location=(960, 1034))
        draw.text(pixel_location, text=name_text, font=name_font, fill=navy_blue_color)

        # add released count and currency earned
        default_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 36)
        draw.text((805, 150), text=f"{self.count_released}", font=default_font, fill=(38, 36, 109))
        draw.text((1170, 150), text=f"{self.currency}", font=default_font, fill=navy_blue_color)

        if len(self.earned_items) == 0:
            no_items_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 48)
            pixel_location = center_text_on_pixel(text="No Items Earned", font=no_items_font, center_pixel_location=(960, 540))
            draw.text(pixel_location, text="No Items Earned", font=no_items_font, fill=navy_blue_color)

        return image

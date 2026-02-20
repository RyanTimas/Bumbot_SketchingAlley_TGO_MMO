from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import *
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import FONT_COLOR_WHITE, FONT_COLOR_DARK_GRAY
from src.resources.constants.file_paths import *


class EncyclopediaXLImageFactory(BaseImageFactory):
    def __init__(self, parent_image_factory=None):
        super().__init__(message_author=parent_image_factory.message_author, target_user=parent_image_factory.target_user)
        self.parent_image_factory = parent_image_factory
        self.dex_icons = []


    def reload_image(self, dex_icons=None):
        self.load_relevant_info(dex_icons=dex_icons)
        return self.build_image()

    def load_relevant_info(self, dex_icons=None):
        self.dex_icons = dex_icons if dex_icons is not None else self.dex_icons

    def build_image(self):
        encyclopedia_img = Image.open(f"{ENCYCLOPEDIA_XL_BACKGROUND_IMAGE}")
        overlay_img = Image.open(f"{ENCYCLOPEDIA_XL_OVERLAY_IMAGE}")
        box_img = Image.open(f"{ENCYCLOPEDIA_XL_BOX_BASE}{self.parent_image_factory.environment.dex_no}{IMAGE_FILE_EXTENSION}")

        icon_dimensions, icons_per_row, total_rows = self.calculate_dex_grid_information(len(self.parent_image_factory.creatures))
        dex_icon_grid = self.build_grid(icons=self.parent_image_factory.dex_icons, grid_size=(2050, 942), icon_size=icon_dimensions, icons_per_page=1000, icons_per_row=icons_per_row, horizontal_padding=1, vertical_padding=1)

        encyclopedia_img.paste(box_img, (0, 0), box_img)
        encyclopedia_img.paste(dex_icon_grid, (743, 109), dex_icon_grid)
        encyclopedia_img = self.add_player_images_to_image(encyclopedia_img)
        encyclopedia_img.paste(overlay_img, (0, 0), overlay_img)

        return self.add_text_to_encyclopedia_image(encyclopedia_img)

    # Calculate optimal icon dimensions for a grid layout.
    # Returns: tuple: ((icon_width, icon_height), icons_per_row, total_rows)
    def calculate_dex_grid_information(self, total_icons = 1000):
        target_grid_width = 2020
        target_grid_height = 942
        min_icons_per_row = 20
        max_icons_per_row = 38
        min_icon_height = 40
        max_icon_height = 75
        padding = 1

        best_config = None
        best_area = 0

        # Try different numbers of icons per row
        for icons_per_row in range(min_icons_per_row, max_icons_per_row + 1):
            total_rows = (total_icons + icons_per_row - 1) // icons_per_row  # Ceiling division

            # Calculate available space for icons (accounting for padding)
            available_width = target_grid_width - (icons_per_row - 1) * padding
            available_height = target_grid_height - (total_rows - 1) * padding

            # Calculate maximum icon dimensions based on available space
            max_icon_width_by_grid = available_width // icons_per_row
            max_icon_height_by_grid = available_height // total_rows

            # Maintain 4:3 ratio (width:height)
            # Try width-constrained approach
            icon_width = max_icon_width_by_grid
            icon_height = int(icon_width * 3 / 4)

            # Check if height constraint is violated
            if icon_height > max_icon_height_by_grid:
                # Use height-constrained approach
                icon_height = max_icon_height_by_grid
                icon_width = int(icon_height * 4 / 3)

            # Ensure icon height is within bounds
            if icon_height < min_icon_height:
                icon_height = min_icon_height
                icon_width = int(icon_height * 4 / 3)
            elif icon_height > max_icon_height:
                icon_height = max_icon_height
                icon_width = int(icon_height * 4 / 3)

            # Calculate actual grid dimensions with this configuration
            actual_width = icons_per_row * icon_width + (icons_per_row - 1) * padding
            actual_height = total_rows * icon_height + (total_rows - 1) * padding

            # Check if this configuration fits within target dimensions
            if actual_width <= target_grid_width and actual_height <= target_grid_height:
                icon_area = icon_width * icon_height
                if icon_area > best_area:
                    best_area = icon_area
                    best_config = ((icon_width, icon_height), icons_per_row, total_rows)

        return best_config if best_config else ((53, 40), 38, (total_icons + 37) // 38)

    def add_player_images_to_image(self, encyclopedia_img: Image):
        # add discord profile pic to image
        # todo: is is_server_view, put the tgommo logo instead of profile pic
        if not self.parent_image_factory.is_server_view:
            profile_pic = build_user_profile_pic(user=self.parent_image_factory.target_user.discord_profile, size=(236, 236))
            encyclopedia_img.paste(profile_pic, (246, 215), profile_pic)

        # add avatar to image
        player_avatar_image = Image.open(f"{PLAYER_PROFILE_AVATAR_BASE}_{self.parent_image_factory.target_user.avatar.avatar_type}_{self.parent_image_factory.target_user.avatar.img_root}{IMAGE_FILE_EXTENSION}")
        player_avatar_image = player_avatar_image.resize((711, 400), Image.LANCZOS)
        encyclopedia_img.paste(player_avatar_image, (9, 520), player_avatar_image)

        return encyclopedia_img


    def add_text_to_encyclopedia_image(self, encyclopedia_img: Image):
        encyclopedia_img = place_username_on_image(target_user=self.parent_image_factory.target_user, image=encyclopedia_img, border_color=(255,0,0), max_width=480, max_font_size=60)
        draw = ImageDraw.Draw(encyclopedia_img)

        bar_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 22)
        bar_font_color = FONT_COLOR_WHITE

        text = f"{'0' if self.parent_image_factory.unique_catches_for_user < 10 else ''} {self.parent_image_factory.unique_catches_for_user} / {'0' if self.parent_image_factory.unique_creatures_available_for_environment < 10 else ''} {self.parent_image_factory.unique_creatures_available_for_environment}"
        pixel_location = (1104, 64)
        draw.text(pixel_location, text=text, font=bar_font, fill=bar_font_color)

        text = f"{self.parent_image_factory.total_user_catches}"
        pixel_location = (1440, 64)
        draw.text(pixel_location, text=text, font=bar_font, fill=bar_font_color)

        # BOTTOM BAR TEXT
        text = f"{self.parent_image_factory.environment.name}"
        font = resize_text_to_fit(text=text, draw=draw, font=bar_font, max_width=225, min_font_size=10)
        pixel_location = center_text_on_pixel(text, font, center_pixel_location=(2160, 73))
        draw.text(pixel_location, text=text, font=font, color=bar_font_color)

        return encyclopedia_img
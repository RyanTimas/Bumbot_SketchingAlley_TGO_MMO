from PIL import Image, ImageDraw

from src.discord.objects.TGOPlayer import TGOPlayer
from src.resources.constants.file_paths import *


class BaseImageFactory:
    """Base class for creating images displayed within the game."""
    def __init__(self, message_author, target_user):
        # User context
        self.message_author: TGOPlayer = message_author
        self.target_user: TGOPlayer = target_user
        self.is_server_view = target_user.user_id == 0

        # Page # state
        self.page_num = 1
        self.total_pages = 1
        self.open_tab = None
        self.grid_icons = []


    '''----IMAGE GENERATION METHODS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # Reload the image with updated parameters.
    def reload_image(self, target_user=None, new_page_number = None):
        self.load_relevant_info(target_user=target_user, new_page_number=new_page_number)
        return self.build_image()
    # Load and update relevant information for image generation. Override this method in subclasses to implement specific data loading.
    def load_relevant_info(self, target_user=None, new_page_number = None):
        self.target_user = target_user if target_user else self.target_user
        self.page_num = new_page_number if new_page_number else self.page_num
        pass
    # Build and return the final image. Override this method in subclasses to implement specific image generation.
    def build_image(self):
        return None

    '''----IMAGE UTILITY METHODS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # Add text to an image using PIL ImageDraw. This is a placeholder method that can be overridden in subclasses to add specific text to images as needed.
    def add_text_to_image(self, img: Image):
        return img

    # Helper function to build a grid of icons with specified parameters, resizing icons as needed and applying padding between them
    def build_grid(self, icons, grid_size=(1920, 1080), icon_size=(500, 70), icons_per_page=10, icons_per_row=3, horizontal_padding=6, vertical_padding=3):
        icon_width, icon_height = icon_size

        # Use centralized pagination helper to obtain the page icons and update page state
        page_icons = self.get_page_icons(icons=icons, icons_per_page=icons_per_page, page=self.page_num)

        grid_canvas = Image.new('RGBA', grid_size, (0, 0, 0, 0))

        row, col = 0, 0
        for icon in page_icons:
            if icon.size != icon_size:
                icon = icon.resize(icon_size, Image.LANCZOS)

            x = col * (icon_width + horizontal_padding)
            y = row * (icon_height + vertical_padding)

            # Use the icon itself as mask if it has an alpha channel
            mask = icon if icon.mode in ("RGBA", "LA") else None
            grid_canvas.paste(icon, (int(x), int(y)), mask)

            col += 1
            if col >= icons_per_row:
                col = 0
                row += 1

        return grid_canvas

    # Return the sublist of icons for open page.
    def get_page_icons(self, icons=None, icons_per_page=25, page=None):
        from math import ceil
        icons = icons if icons is not None else self.grid_icons
        self.total_pages = max(1, ceil(len(icons) / icons_per_page))

        page = page if page is not None else self.page_num
        page = max(1, min(page, self.total_pages))
        self.page_num = page
        start = (page - 1) * icons_per_page
        end = start + icons_per_page
        return icons[start:end]

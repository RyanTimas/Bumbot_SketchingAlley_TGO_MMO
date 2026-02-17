from PIL import Image, ImageDraw

from src.discord.objects.TGOPlayer import TGOPlayer
from src.resources.constants.file_paths import *


class BaseImageFactory:
    def __init__(self, message_author, target_user):
        self.message_author: TGOPlayer = message_author
        self.target_user: TGOPlayer = target_user
        self.is_server_view = target_user.user_id == 0

        self.page_num = 1
        self.total_pages = 1

    def reload_image(self, new_page_number = None):
        self.load_relevant_info(new_page_number)
        return self.build_image()
    def load_relevant_info(self, new_page_number = None):
        self.page_num = new_page_number if new_page_number else self.page_num
        pass
    def build_image(self):
        return None


# SUPPORT FUNCTIONS
    def add_text_to_image(self, img: Image):
        draw = ImageDraw.Draw(img)
        return img

    def build_grid(self, icons, grid_size=(1920, 1080), icon_size=(500, 70), icons_per_row=3, horizontal_padding=6, vertical_padding=3):
        grid_canvas = Image.new('RGBA', grid_size, (0, 0, 0, 0))
        icon_width, icon_height = icon_size

        # Calculate padding
        row, col = 0, 0

        for i, icon in enumerate(icons):
            # Calculate position
            x = col * (icon_width + horizontal_padding if i != 0 else 0)
            y = row * (icon_height + vertical_padding if i != 0 else 0)

            # Paste icon onto canvas
            grid_canvas.paste(icon, (int(x), int(y)), icon)

            # Move to next position
            col += 1
            if col >= icons_per_row:
                col = 0
                row += 1

        return grid_canvas






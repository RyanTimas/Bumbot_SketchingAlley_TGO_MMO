from PIL import Image, ImageDraw

from src.discord.objects.TGOPlayer import TGOPlayer
from src.resources.constants.file_paths import *


class BaseImageFactory:
    def __init__(self, message_author, target_user):
        self.message_author: TGOPlayer = message_author
        self.target_user: TGOPlayer = target_user

        self.page_num = 1
        self.total_pages = 1

        self.load_relevant_info()

    def load_relevant_info(self, new_page_number = None):
        self.page_num = new_page_number if new_page_number else self.page_num
        pass

    def reload_image(self, new_page_number = 1):
        self.load_relevant_info()
        return self.build_image()


    '''IMAGE FUNCTIONS'''
    def build_image(self):
        return self.add_text_to_image(Image.open(AVATAR_BOARD_BACKGROUND_IMAGE))

    def add_text_to_image(self, img: Image):
        draw = ImageDraw.Draw(img)
        return img





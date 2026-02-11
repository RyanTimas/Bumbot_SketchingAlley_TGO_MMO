from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarQuestTabFactory import AvatarQuestTabFactory
from src.discord.game_features.avatar_board.UnlockedAvatarIconFactory import UnlockedAvatarIconFactory
from src.resources.constants.file_paths import *


class BaseImageFactory:
    def __init__(self, message_author, target_user):
        self.message_author = message_author
        self.target_user = target_user

        self.page_num = 1
        self.total_pages = 1

        self.load_relevant_info()

    def load_relevant_info(self):
        # Load initial page info
        pass

    def reload_image(self, new_page_number = None):
        # update components
        self.page_num = new_page_number if new_page_number else self.page_num

        return self.build_image()


    '''IMAGE FUNCTIONS'''
    def build_image(self):
        # define images
        new_img = Image.open(AVATAR_BOARD_BACKGROUND_IMAGE)

        # paste images together
        new_img = self.add_text_to_image(new_img)

        return new_img

    def add_text_to_image(self, img: Image):
        draw = ImageDraw.Draw(img)

        # define fonts
        # add piece of text to image

        return img





from PIL import Image

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarBoardAvatarQuestImageFactory import AvatarBoardAvatarQuestImageFactory
from src.discord.game_features.avatar_board.AvatarBoardUnlockedAvatarImageFactory import \
    AvatarBoardUnlockedAvatarImageFactory
from src.discord.game_features.avatar_board.UnlockedAvatarIconFactory import UnlockedAvatarIconFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import AVATAR_TYPE_SORT_ORDER, AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY
from src.resources.constants.file_paths import *


class AvatarBoardImageFactory(BaseImageFactory):
    def __init__(self, message_author, target_user, open_tab="unlocked_avatars"):
        super().__init__(message_author=message_author, target_user=target_user)

        self.open_tab = open_tab
        self.avatar_board_unlocked_avatar_image_factory = AvatarBoardUnlockedAvatarImageFactory(message_author, target_user)
        self.avatar_board_quest_image_factory = AvatarBoardAvatarQuestImageFactory(message_author, target_user)

        # Set initial page_num based on active factory
        self.page_num = self.get_active_image_factory().page_num
        self.total_pages = self.get_active_image_factory().total_pages



    def load_relevant_info(self, target_user=None, new_page_number=None, open_tab=None):
        self.target_user = target_user if target_user else self.target_user

        # Handle tab switching
        if open_tab and open_tab != self.open_tab:
            self.open_tab = open_tab if open_tab else self.open_tab
            self.total_pages = self.get_active_image_factory().total_pages
            # Reset to page 1 when switching tabs unless specified
            if new_page_number is None:
                new_page_number = 1
        elif open_tab:
            self.open_tab = open_tab

        # Update page number if specified
        if new_page_number is not None:
            self.page_num = new_page_number
            self.get_active_image_factory().page_num = new_page_number

        # Update both factories with relevant info
        self.avatar_board_unlocked_avatar_image_factory.load_relevant_info(target_user=target_user)
        self.avatar_board_quest_image_factory.load_relevant_info(target_user=target_user)

    def build_image(self):
        return self.get_active_image_factory().build_image()

    def reload_image(self, target_user=None, new_page_number=None, open_tab=None):
        self.load_relevant_info(target_user=target_user, new_page_number=new_page_number, open_tab=open_tab)
        return self.build_image()

# ----GETTERS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def get_active_image_factory(self):
        return self.avatar_board_unlocked_avatar_image_factory if self.open_tab == AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY else self.avatar_board_quest_image_factory
    def get_page_num(self):
        return self.get_active_image_factory().page_num
    def get_total_pages(self):
        return self.get_active_image_factory().total_pages

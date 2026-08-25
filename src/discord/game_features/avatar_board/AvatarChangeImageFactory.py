from PIL import Image

from src.discord.game_features.avatar_board.AvatarBoardAvatarQuestImageFactory import AvatarBoardAvatarQuestImageFactory
from src.discord.game_features.avatar_board.AvatarBoardUnlockedAvatarImageFactory import AvatarBoardUnlockedAvatarImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import AVATAR_TYPE_SORT_ORDER, AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY
from src.resources.constants.file_paths import CREATURE_INVENTORY_RELEASE_SUMMARY_BG_IMAGE


class AvatarChangeImageFactory(BaseImageFactory):
    def __init__(self, message_author, target_user):
        super().__init__(message_author=message_author, target_user=target_user)


    def reload_image(self, target_user=None, new_page_number=None):
        self.load_relevant_info(target_user= target_user, new_page_number=new_page_number)
        return self.build_image()
    def load_relevant_info(self, target_user=None, new_page_number=None):
        self.target_user = target_user if target_user else self.target_user

        # reset page number to 1 unless a new_page_number is provided
        self.page_num = new_page_number if new_page_number else 1

    def build_image(self):
        return Image.open(CREATURE_INVENTORY_RELEASE_SUMMARY_BG_IMAGE)
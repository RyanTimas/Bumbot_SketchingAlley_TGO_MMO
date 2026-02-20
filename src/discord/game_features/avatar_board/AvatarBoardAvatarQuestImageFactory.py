from PIL import Image

from src.commons.CommonFunctions import convert_to_png, interaction_guard
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarQuestTabFactory import AvatarQuestTabFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.file_paths import *


class AvatarBoardAvatarQuestImageFactory(BaseImageFactory):
    def __init__(self, message_author, target_user):
        self.avatar_quest_icons = []
        self.avatar_quests = get_tgommo_db_handler().get_avatars_with_unlock_conditions()

        super().__init__(message_author=message_author, target_user=target_user)
        self.total_pages = len(self.avatar_quests) // 18 + (1 if len(self.avatar_quests) % 18 > 0 else 0)
        self.load_relevant_info()

    def load_relevant_info(self, target_user=None, new_page_number = None):
        super().load_relevant_info(target_user=target_user, new_page_number=new_page_number)
        self.avatar_quest_icons = self.get_avatar_quests_icons()
    def build_image(self, target_user=None, new_page_number = None, open_tab = None):
        avatar_quest_img = Image.open(AVATAR_BOARD_BACKGROUND_IMAGE)
        corner_overlay_img = Image.open(AVATAR_BOARD_CORNER_OVERLAY)
        unlocked_avatar_button_img = Image.open(AVATAR_BOARD_BUTTON_UNLOCKED_AVATAR_INACTIVE_IMAGE)
        avatar_quest_button_img = Image.open(AVATAR_BOARD_BUTTON_AVATAR_QUESTS_ACTIVE_IMAGE)

        starting_index = (self.page_num - 1) * 16
        ending_index = min(starting_index + 16, len(self.avatar_quest_icons))
        avatar_quest_grid_img = self.build_grid(self.avatar_quest_icons[starting_index:ending_index], grid_size=(1092, 476), icon_size=(550, 50), icons_per_page=16, icons_per_row=2, horizontal_padding=0, vertical_padding=5)

        avatar_quest_img.paste(unlocked_avatar_button_img, (0, 0), unlocked_avatar_button_img)
        avatar_quest_img.paste(avatar_quest_button_img, (0, 0), avatar_quest_button_img)
        avatar_quest_img.paste(avatar_quest_grid_img, (103, 100), avatar_quest_grid_img)
        avatar_quest_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)
        return avatar_quest_img

    def get_avatar_quests_icons(self):
        if len(self.avatar_quests) == 0:
            return None

        imgs = []
        raw_imgs = []

        # Only process creatures within our page range
        for i, avatar in enumerate(self.avatar_quests):
            if avatar.is_secret:
                continue

            avatar_quest = AvatarQuestTabFactory(avatar=avatar, user_id=self.target_user.user_id)
            avatar_quest_img = avatar_quest.generate_avatar_quest_tab_image()

            raw_imgs.append(avatar_quest_img)
            imgs.append(convert_to_png(avatar_quest_img, f'avatar_icon_{avatar.img_root}.png'))

        return raw_imgs  #, imgs

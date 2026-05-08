from PIL import Image

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarQuestTabFactory import AvatarQuestTabFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import AVATAR_BOARD_SORT_AVATAR_TYPE, AVATAR_TYPE_SORT_ORDER
from src.resources.constants.file_paths import *


class AvatarBoardAvatarQuestImageFactory(BaseImageFactory):
    def __init__(self, message_author, target_user):
        super().__init__(message_author=message_author, target_user=target_user)

        self.avatars_with_quests = self.get_avatars_with_quests()

        # sorting / filtering options
        self.display_completed_quests = False
        self.order_type = AVATAR_BOARD_SORT_AVATAR_TYPE
        self.is_ascending_order = False
        self.is_exclusive_mode = False

        self.total_pages = len(self.avatars_with_quests) // 18 + (1 if len(self.avatars_with_quests) % 18 > 0 else 0)
        self.load_relevant_info()

    def load_relevant_info(self, target_user=None, new_page_number = None, display_completed_quests=None):
        super().load_relevant_info(target_user=target_user, new_page_number=new_page_number)
        self.display_completed_quests = display_completed_quests if display_completed_quests is not None else self.display_completed_quests
    def build_image(self, target_user=None, new_page_number = None, open_tab = None):
        avatar_quest_img = Image.open(AVATAR_BOARD_BACKGROUND_IMAGE)
        corner_overlay_img = Image.open(AVATAR_BOARD_CORNER_OVERLAY)
        unlocked_avatar_button_img = Image.open(AVATAR_BOARD_BUTTON_UNLOCKED_AVATAR_INACTIVE_IMAGE)
        avatar_quest_button_img = Image.open(AVATAR_BOARD_BUTTON_AVATAR_QUESTS_ACTIVE_IMAGE)

        avatar_quest_grid_img = self.build_grid(self.get_avatar_quests_for_grid(), grid_size=(1092, 476), icon_size=(550, 50), icons_per_page=16, icons_per_row=2, horizontal_padding=0, vertical_padding=5)

        avatar_quest_img.paste(unlocked_avatar_button_img, (0, 0), unlocked_avatar_button_img)
        avatar_quest_img.paste(avatar_quest_button_img, (0, 0), avatar_quest_button_img)
        avatar_quest_img.paste(avatar_quest_grid_img, (103, 100), avatar_quest_grid_img)
        avatar_quest_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)
        return avatar_quest_img

    def get_avatars_with_quests(self):
        avatars_with_quests = get_tgommo_db_handler().get_avatars_with_unlock_conditions()
        for avatar_with_quest in avatars_with_quests:
            if not avatar_with_quest.is_secret:
                avatar_quest_tab_factory = AvatarQuestTabFactory(avatar=avatar_with_quest, user_id=self.target_user.user_id)

                avatar_with_quest.is_completed = avatar_quest_tab_factory.is_completed
                avatar_with_quest.quest_progress_icon = avatar_quest_tab_factory.generate_avatar_quest_tab_image()
        return avatars_with_quests

    def get_avatar_quests_for_grid(self):
        max_icons_per_page = 16
        avatar_quests_for_page = self.avatars_with_quests

        # First step is to filter the avatar quests based on whether we want to display completed quests or not
        # Filter based on quest completion status
        avatar_quests_for_page = [quest for quest in avatar_quests_for_page if (quest.is_completed == self.is_exclusive_mode  if self.display_completed_quests else True)]

        # Then slice the list to get only the quests for the current page
        starting_index = (self.page_num - 1) * max_icons_per_page
        ending_index = min(starting_index + max_icons_per_page, len(avatar_quests_for_page))
        avatar_quests_for_page = avatar_quests_for_page[starting_index:ending_index]

        # Apply sorting based on the selected order type and sort direction
        sort_options = {
            AVATAR_BOARD_SORT_AVATAR_TYPE: lambda av: (AVATAR_TYPE_SORT_ORDER.get(av.avatar_type, 999), av.avatar_num)
        }

        if self.order_type in sort_options:
            avatar_quests_for_page.sort(key=sort_options[self.order_type], reverse= self.is_ascending_order)

        return [avatar.quest_progress_icon for avatar in avatar_quests_for_page if avatar.quest_progress_icon is not None]
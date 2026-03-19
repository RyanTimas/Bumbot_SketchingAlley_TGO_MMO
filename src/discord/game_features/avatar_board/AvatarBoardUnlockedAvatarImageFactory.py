from PIL import Image

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class AvatarBoardUnlockedAvatarImageFactory(BaseImageFactory):
    def __init__(self, message_author, target_user):
        super().__init__(message_author=message_author, target_user=target_user)

        self.unlocked_avatars = self.get_unlocked_avatars()

        # sorting / filtering options
        self.order_type = AVATAR_BOARD_SORT_AVATAR_TYPE
        self.is_ascending_order = False

        self.load_relevant_info()
        self.total_pages = len(self.unlocked_avatars) // 75 + (1 if len(self.unlocked_avatars) % 75 > 0 else 0)

    def load_relevant_info(self, target_user=None, new_page_number = None, order_type=None, is_ascending_order=None):
        super().load_relevant_info(target_user=target_user, new_page_number=new_page_number)
        self.order_type = order_type if order_type is not None else self.order_type
        self.is_ascending_order = is_ascending_order if is_ascending_order is not None else self.is_ascending_order

        if target_user:
            self.unlocked_avatars = self.get_unlocked_avatars()
    def build_image(self):
        avatar_board_img = Image.open(AVATAR_BOARD_BACKGROUND_IMAGE)
        corner_overlay_img = Image.open(AVATAR_BOARD_CORNER_OVERLAY)
        unlocked_avatar_button_img = Image.open(AVATAR_BOARD_BUTTON_UNLOCKED_AVATAR_ACTIVE_IMAGE)
        avatar_quest_button_img = Image.open(AVATAR_BOARD_BUTTON_AVATAR_QUESTS_INACTIVE_IMAGE)

        unlocked_avatars_grid_img = self.build_grid(self.get_avatars_for_grid(), grid_size=(1092, 476), icon_size=(70, 90), icons_per_page=75, icons_per_row=15, horizontal_padding=1, vertical_padding=1)

        avatar_board_img.paste(unlocked_avatar_button_img, (0, 0), unlocked_avatar_button_img)
        avatar_board_img.paste(avatar_quest_button_img, (0, 0), avatar_quest_button_img)
        avatar_board_img.paste(unlocked_avatars_grid_img, (102, 106), unlocked_avatars_grid_img)
        avatar_board_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)
        return avatar_board_img


    # retrieve the list of unlocked avatars for the target user, including avatars unlocked by all users and avatars unlocked specifically by the target user, then sort the list based on avatar type and avatar number
    def get_unlocked_avatars(self):
        # first add avatars unlocked by all users to the list, then add avatars unlocked by the target user
        unlocked_avatars = get_tgommo_db_handler().get_unlocked_avatars_by_user_id(-1)
        unlocked_avatars += get_tgommo_db_handler().get_unlocked_avatars_by_user_id(self.target_user.user_id)

        # by default, sort avatars by avatar type and then by avatar number within each type, with unknown types sorted at the end
        unlocked_avatars.sort(key=lambda avatar: (
            AVATAR_TYPE_SORT_ORDER.get(avatar.avatar_type, 999),
            avatar.avatar_num
        ))

        return unlocked_avatars

    # method to get the avatar icons for the current page of unlocked avatars, based on the current sorting and filtering options
    def get_avatars_for_grid(self):
        max_icons_per_page = 75

        start_index = (self.page_num - 1) * max_icons_per_page
        end_index = start_index + max_icons_per_page
        avatars_for_page = self.unlocked_avatars[start_index:end_index]

        # todo: add filtering options in future - option to show only avatars of a certain series, or type, or to add the ability to favorite avatars

        # Apply sorting based on the selected order type and sort direction
        sort_options = {
            AVATAR_BOARD_SORT_ALPHABETICAL: lambda av: av.name,
            AVATAR_BOARD_SORT_DEX_NO: lambda av: av.avatar_num,
            AVATAR_BOARD_SORT_SERIES: lambda av: (av.series, av.avatar_num),
            AVATAR_BOARD_SORT_AVATAR_TYPE: lambda av: (AVATAR_TYPE_SORT_ORDER.get(av.avatar_type, 999), av.avatar_num)
        }
        if self.order_type in sort_options:
            avatars_for_page.sort(
                key=sort_options[self.order_type],
                reverse= self.is_ascending_order
            )

        return [avatar.unlocked_avatar_icon for avatar in avatars_for_page]
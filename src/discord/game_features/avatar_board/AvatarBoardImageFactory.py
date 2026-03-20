from src.discord.game_features.avatar_board.AvatarBoardAvatarQuestImageFactory import AvatarBoardAvatarQuestImageFactory
from src.discord.game_features.avatar_board.AvatarBoardUnlockedAvatarImageFactory import AvatarBoardUnlockedAvatarImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import AVATAR_TYPE_SORT_ORDER, AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY


class AvatarBoardImageFactory(BaseImageFactory):
    def __init__(self, message_author, target_user, open_tab="unlocked_avatars"):
        super().__init__(message_author=message_author, target_user=target_user)

        self.open_tab = open_tab
        self.avatar_board_unlocked_avatar_image_factory = AvatarBoardUnlockedAvatarImageFactory(message_author, target_user)
        self.avatar_board_quest_image_factory = AvatarBoardAvatarQuestImageFactory(message_author, target_user)

        # Set initial page_num based on active factory
        self.page_num = self.get_active_image_factory().page_num
        self.total_pages = self.get_active_image_factory().total_pages

    def reload_image(self, target_user=None, new_page_number=None, open_tab=None, order_type=None, is_ascending_order=None, is_exclusive_mode=None):
        self.load_relevant_info(target_user= target_user, new_page_number=new_page_number, open_tab=open_tab, order_type=order_type, is_ascending_order=is_ascending_order, is_exclusive_mode=is_exclusive_mode)
        return self.build_image()
    def load_relevant_info(self, target_user=None, new_page_number=None, open_tab=None, order_type=None, is_ascending_order=None, is_exclusive_mode=None):
        self.target_user = target_user if target_user else self.target_user
        self.get_active_image_factory().order_type = order_type if order_type is not None else self.get_active_image_factory().order_type
        self.get_active_image_factory().is_ascending_order = is_ascending_order if is_ascending_order is not None else self.get_active_image_factory().is_ascending_order
        self.get_active_image_factory().is_exclusive_mode = is_exclusive_mode if is_exclusive_mode is not None else self.get_active_image_factory().is_exclusive_mode

        # Handle tab switching
        if open_tab:
            self.open_tab = open_tab
            # if the tab is changed, update total_pages and reset page number to 1 unless specified otherwise
            if open_tab != self.open_tab:
                self.total_pages = self.get_active_image_factory().total_pages
                new_page_number = new_page_number if new_page_number else 1
        if new_page_number:
            self.page_num = new_page_number
            self.get_active_image_factory().page_num = new_page_number

        # Update both factories with relevant info
        self.avatar_board_unlocked_avatar_image_factory.load_relevant_info(target_user=target_user)
        self.avatar_board_quest_image_factory.load_relevant_info(target_user=target_user)
    def build_image(self):
        return self.get_active_image_factory().build_image()

    # ----GETTERS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def get_active_image_factory(self):
        return self.avatar_board_unlocked_avatar_image_factory if self.open_tab == AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY else self.avatar_board_quest_image_factory
    def get_page_num(self):
        return self.get_active_image_factory().page_num
    def get_total_pages(self):
        return self.get_active_image_factory().total_pages
    def get_order_type(self):
        return self.get_active_image_factory().order_type
    def get_is_ascending_order(self):
        return self.get_active_image_factory().is_ascending_order

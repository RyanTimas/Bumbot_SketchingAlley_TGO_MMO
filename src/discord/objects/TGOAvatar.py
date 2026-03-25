from random import randint

from PIL import Image
from src.resources.constants.file_paths import *


class TGOAvatar:
    def __init__(self,
                 avatar_num:int, avatar_id:str,
                 name:str, series:str,
                 avatar_type:str, is_parent_entry:bool,
                 img_root:str,
                 unlock_query:str ="", unlock_threshold:int =0, is_secret:bool =False
    ):
        self.avatar_num = avatar_num
        self.avatar_id = avatar_id

        self.name = name
        self.series = series

        self.avatar_type = avatar_type

        self.img_root = img_root
        self.is_parent_entry = is_parent_entry

        self.unlock_query = unlock_query if unlock_query else ""
        self.unlock_threshold = unlock_threshold if unlock_threshold else 0
        self.is_secret = is_secret if is_secret else False
        self.is_completed = False

        self.shop_price = 0
        self.last_purchase_date = None

        # base images representing an avatar, represent the full avatar and a headshot
        self.avatar_image = None
        self.avatar_thumbnail_image = None
        self.quest_icon_image = None

        # images for avatar board, represent an icon for the unlocked avatar and an icon for the avatar quest if it exists
        self.unlocked_avatar_icon = None
        self.quest_progress_icon = None

        self.define_avatar_images()

    def define_avatar_images(self):
        from src.discord.game_features.avatar_board.UnlockedAvatarIconFactory import UnlockedAvatarIconFactory

        avatar_img_path = f"{PLAYER_PROFILE_AVATAR_BASE}_{self.avatar_type}_{self.img_root}{IMAGE_FILE_EXTENSION}"
        fallback_img_root_path = f"{PLAYER_PROFILE_AVATAR_BASE}_Fallback-{randint(1,2)}{IMAGE_FILE_EXTENSION}"

        avatar_icon_img_path = f"{AVATAR_BOARD_UNLOCKED_AVATAR_THUMBNAIL_BASE}_{self.img_root}{IMAGE_FILE_EXTENSION}"
        fallback_icon_img_root_path = f"{AVATAR_BOARD_UNLOCKED_AVATAR_THUMBNAIL_BASE}_Fallback-{randint(1, 2)}{IMAGE_FILE_EXTENSION}"

        with Image.open(avatar_img_path if os.path.exists(avatar_img_path) else fallback_img_root_path) as img:
            self.avatar_image = img.copy()
        with Image.open(avatar_icon_img_path if os.path.exists(avatar_icon_img_path) else fallback_icon_img_root_path) as img:
            self.avatar_thumbnail_image = img.copy()

        quest_icon_img_path = f'{AVATAR_QUEST_BASE}_{self.img_root}{IMAGE_FILE_EXTENSION}'
        if os.path.exists(quest_icon_img_path):
            with Image.open(quest_icon_img_path) as img:
                self.quest_icon_image = img.copy()

        self.unlocked_avatar_icon = UnlockedAvatarIconFactory(avatar=self).generate_avatar_quest_tab_image()
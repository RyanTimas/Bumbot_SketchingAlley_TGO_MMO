from PIL import Image

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.UnlockedAvatarIconFactory import UnlockedAvatarIconFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.file_paths import *

AVATAR_QUESTS = "AVATAR_QUESTS"
UNLOCKED_AVATARS = "UNLOCKED_AVATARS"

class AvatarBoardUnlockedAvatarImageFactory(BaseImageFactory):
    def __init__(self, message_author, target_user):
        self.unlocked_avatar_icons = []
        self.unlocked_avatars = get_tgommo_db_handler().get_unlocked_avatars_by_user_id(target_user.user_id, convert_to_object=True)

        super().__init__(message_author=message_author, target_user=target_user)
        self.total_pages = len(self.unlocked_avatars) // 75 + (1 if len(self.unlocked_avatars) % 75 > 0 else 0)
        self.load_relevant_info()

    def load_relevant_info(self, new_page_number = None):
        self.page_num = new_page_number if new_page_number else self.page_num
        self.unlocked_avatar_icons = self.get_unlocked_avatars_icons()
    def build_image(self):
        avatar_board_img = Image.open(AVATAR_BOARD_BACKGROUND_IMAGE)
        corner_overlay_img = Image.open(AVATAR_BOARD_CORNER_OVERLAY)
        unlocked_avatar_button_img = Image.open(AVATAR_BOARD_BUTTON_UNLOCKED_AVATAR_ACTIVE_IMAGE)
        avatar_quest_button_img = Image.open(AVATAR_BOARD_BUTTON_AVATAR_QUESTS_INACTIVE_IMAGE)

        unlocked_avatars_grid_img = self.create_unlocked_avatars_grid()

        avatar_board_img.paste(unlocked_avatar_button_img, (0, 0), unlocked_avatar_button_img)
        avatar_board_img.paste(avatar_quest_button_img, (0, 0), avatar_quest_button_img)
        avatar_board_img.paste(unlocked_avatars_grid_img, (102, 106), unlocked_avatars_grid_img)
        avatar_board_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)
        return avatar_board_img


    # Unlocked Avatars Section
    def get_unlocked_avatars_icons(self):
        if len(self.unlocked_avatars) == 0:
            return None

        imgs = []
        raw_imgs = []
        icons_per_page = 75

        starting_index = (self.page_num - 1) * icons_per_page
        ending_index = min(starting_index + icons_per_page, len(self.unlocked_avatars))  # Ensure we don't go past the end of the list

        # Only process avatars within our page range
        for i in range(starting_index, ending_index):
            avatar = self.unlocked_avatars[i]
            avatar_icon = UnlockedAvatarIconFactory(avatar=avatar)
            unlocked_avatar_icon_img = avatar_icon.generate_avatar_quest_tab_image()

            raw_imgs.append(unlocked_avatar_icon_img)
            imgs.append(convert_to_png(unlocked_avatar_icon_img, f'creature_icon_{avatar.avatar_id}_{avatar.name}.png'))

        return raw_imgs  #, imgs
    def create_unlocked_avatars_grid(self):
        # Create a blank canvas for the grid
        grid_canvas = Image.new('RGBA', (1092, 476), (0, 0, 0, 0))

        # Define grid parameters
        icon_width, icon_height = 70, 90
        icons_per_row = 15

        # Define parameters for which icons will appear on page
        icons_per_page = 75
        starting_index = (self.page_num - 1) * icons_per_page
        ending_index = min(starting_index + icons_per_page, len(self.unlocked_avatars))

        # Calculate padding
        horizontal_padding = 1
        vertical_padding = 1

        # Place icons in grid
        row, col = 0, 0
        for i in range(starting_index, ending_index):
            avatar_icon = self.unlocked_avatar_icons[i]
            # Calculate position
            x = col * (icon_width + horizontal_padding if i != 0 else 0)
            y = row * (icon_height + vertical_padding if i != 0 else 0)

            # Paste icon onto canvas
            grid_canvas.paste(avatar_icon, (int(x), int(y)))

            # Move to next position
            col += 1
            if col >= icons_per_row:
                col = 0
                row += 1

            # Stop if we run out of space
            if row * (icon_height + vertical_padding) + icon_height > 500:
                break

        return grid_canvas
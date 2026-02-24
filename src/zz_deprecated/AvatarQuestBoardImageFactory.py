from PIL import Image

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarQuestTabFactory import AvatarQuestTabFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.discord.objects.TGOPlayer import TGOPlayer
from src.resources.constants.file_paths import *

class AvatarQuestBoardImageFactory(BaseImageFactory):
    def __init__(self, message_author: TGOPlayer, target_user: TGOPlayer):
        super().__init__(message_author, target_user)

        self.avatar_quests = get_tgommo_db_handler().get_avatars_with_unlock_conditions()

        self.page_num = 1
        self.total_pages = len(self.avatar_quests) // 18 + (1 if len(self.avatar_quests) % 18 > 0 else 0)
        self.avatar_quest_icons = self.get_avatar_quests_icons()

        self.load_relevant_info()


    def reload_image(self, new_page_number = None):
        return super().reload_image(new_page_number)

    def build_image(self, new_page_number = None):
        # construct images
        new_img = Image.open(AVATAR_BOARD_BACKGROUND_IMAGE)
        corner_overlay_img = Image.open(AVATAR_BOARD_CORNER_OVERLAY)

        unlocked_avatar_button_img = Image.open(AVATAR_BOARD_BUTTON_UNLOCKED_AVATAR_INACTIVE_IMAGE)
        avatar_quest_button_img = Image.open(AVATAR_BOARD_BUTTON_AVATAR_QUESTS_ACTIVE_IMAGE)
        avatar_quests_grid_img = self.create_avatar_quests_grid()

        # paste images together
        new_img.paste(unlocked_avatar_button_img, (0, 0), unlocked_avatar_button_img)
        new_img.paste(avatar_quest_button_img, (0, 0), avatar_quest_button_img)
        new_img.paste(avatar_quests_grid_img, (103, 100), avatar_quests_grid_img)
        new_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)

        return new_img

    def build_avatar_quests_page(self, img):
        avatar_quests_grid_img = self.create_avatar_quests_grid()

        return img.paste(avatar_quests_grid_img, (103, 100), avatar_quests_grid_img)

    def get_avatar_quests_icons(self):
        if len(self.avatar_quests) == 0:
            return None

        imgs = []
        raw_imgs = []

        for i, avatar in enumerate(self.avatar_quests):
            if avatar.is_secret:
                continue

            avatar_quest = AvatarQuestTabFactory(avatar=avatar, user_id=self.target_user.user_id)
            avatar_quest_img = avatar_quest.generate_avatar_quest_tab_image()

            raw_imgs.append(avatar_quest_img)
            imgs.append(convert_to_png(avatar_quest_img, f'avatar_icon_{avatar.avatar_id}.png'))

        return raw_imgs  #, imgs

    def create_avatar_quests_grid(self):
        # Create a blank canvas for the grid
        grid_canvas = Image.new('RGBA', (1092, 476), (0, 0, 0, 0))

        # Define grid parameters
        icon_width, icon_height = 550, 50
        icons_per_row = 2

        # Calculate padding
        horizontal_padding = 0
        vertical_padding = 5

        # Define how many icons will be displayed at a time
        tabs_per_page = 16
        starting_index = (self.page_num - 1) * tabs_per_page  # Adjust calculation to start from 0
        ending_index = min(starting_index + tabs_per_page, len(self.avatar_quest_icons))  # Ensure we don't go past the end of the list

        # Place icons on grid
        row, col = 0, 0
        for i in range(starting_index, ending_index):
            dex_icon = self.avatar_quest_icons[i]

            # Calculate position
            x = col * (icon_width + horizontal_padding if i != 0 else 0)
            y = row * (icon_height + vertical_padding if i != 0 else 0)

            # Paste icon onto canvas
            grid_canvas.paste(dex_icon, (int(x), int(y)))

            # Move to next position
            col += 1
            if col >= icons_per_row:
                col = 0
                row += 1

            # Stop if we run out of space
            if row * (icon_height + vertical_padding) + icon_height > 500:
                break

        return grid_canvas


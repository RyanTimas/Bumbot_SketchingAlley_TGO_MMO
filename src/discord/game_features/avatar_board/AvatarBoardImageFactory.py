from PIL import Image

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarQuestTabFactory import AvatarQuestTabFactory
from src.discord.game_features.avatar_board.UnlockedAvatarIconFactory import UnlockedAvatarIconFactory
from src.resources.constants.file_paths import *

AVATAR_QUESTS = "AVATAR_QUESTS"
UNLOCKED_AVATARS = "UNLOCKED_AVATARS"

class AvatarBoardImageFactory:
    def __init__(self, user_id, open_tab):
        self.user_id = user_id

        self.open_tab = open_tab

        self.unlocked_avatars = []
        self.avatar_quests = []

        self.avatar_quest_icons = []
        self.unlocked_avatar_icons = []

        self.page_num_unlocked_avatar = 1
        self.page_num_avatar_quests = 1
        self.total_unlocked_avatar_pages = 1
        self.total_avatar_quest_pages = 1

        self.load_relevant_info()

    def load_relevant_info(self):
        # Load page info for both sections
        self.unlocked_avatars = get_tgommo_db_handler().get_unlocked_avatars_by_user_id(self.user_id, convert_to_object=True)
        self.page_num_unlocked_avatar = 1
        self.total_unlocked_avatar_pages = len(self.unlocked_avatars) // 75 + (1 if len(self.unlocked_avatars) % 75 > 0 else 0)

        self.avatar_quests = get_tgommo_db_handler().get_avatar_unlock_conditions(convert_to_object=True)
        self.page_num_avatar_quests = 1
        self.total_avatar_quest_pages = len(self.avatar_quests) // 18 + (1 if len(self.avatar_quests) % 18 > 0 else 0)

        # load all unlocked avatar icons
        self.unlocked_avatar_icons = self.get_unlocked_avatars_icons()
        self.avatar_quest_icons = self.get_avatar_quests_icons()


    def build_avatar_board_page_image(self, new_page_number = None, open_tab = None):
        # set new values in case button was clicked
        self.open_tab = open_tab if open_tab is not None else self.open_tab
        if new_page_number:
            if self.open_tab == UNLOCKED_AVATARS:
                self.page_num_unlocked_avatar = new_page_number
            elif self.open_tab == AVATAR_QUESTS:
                self.page_num_avatar_quests = new_page_number

        # construct base layers, start with environment bg
        background_img = Image.open(AVATAR_BOARD_BACKGROUND_IMAGE)
        corner_overlay_img = Image.open(AVATAR_BOARD_CORNER_OVERLAY)
        unlocked_avatar_button_img = Image.open(AVATAR_BOARD_BUTTON_UNLOCKED_AVATAR_ACTIVE_IMAGE if self.open_tab == UNLOCKED_AVATARS else AVATAR_BOARD_BUTTON_UNLOCKED_AVATAR_INACTIVE_IMAGE)
        avatar_quest_button_img = Image.open(AVATAR_BOARD_BUTTON_AVATAR_QUESTS_ACTIVE_IMAGE if self.open_tab == AVATAR_QUESTS else AVATAR_BOARD_BUTTON_AVATAR_QUESTS_INACTIVE_IMAGE)

        background_img.paste(unlocked_avatar_button_img, (0, 0), unlocked_avatar_button_img)
        background_img.paste(avatar_quest_button_img, (0, 0), avatar_quest_button_img)

        if self.open_tab == UNLOCKED_AVATARS:
            background_img = self.build_unlocked_avatars_section(background_img)
        elif self.open_tab == AVATAR_QUESTS:
            background_img = self.build_avatar_quests_page(background_img)

        background_img.paste(corner_overlay_img, (0, 0), corner_overlay_img)
        return background_img


    # Unlocked Avatars Section
    def build_unlocked_avatars_section(self, background_img):
        unlocked_avatars_grid_img = self.create_unlocked_avatars_grid()
        background_img.paste(unlocked_avatars_grid_img, (102, 106), unlocked_avatars_grid_img)

        return background_img

    def get_unlocked_avatars_icons(self, page_swap = 0):
        if len(self.unlocked_avatars) == 0:
            return None

        self.page_num_unlocked_avatar += page_swap

        imgs = []
        raw_imgs = []
        icons_per_page = 75

        starting_index = (self.page_num_unlocked_avatar - 1) * icons_per_page
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
        starting_index = (self.page_num_unlocked_avatar - 1) * icons_per_page
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


    # Avatar Quests Section
    def build_avatar_quests_page(self, background_img):
        self.avatar_quest_icons = self.avatar_quest_icons if self.avatar_quest_icons else self.get_avatar_quests_icons()
        avatar_quests_grid_img = self.create_avatar_quests_grid()

        background_img.paste(avatar_quests_grid_img, (103, 100), avatar_quests_grid_img)

        return background_img

    def get_avatar_quests_icons(self, page_swap = 0):
        if len(self.avatar_quests) == 0:
            return None

        self.page_num_avatar_quests += page_swap

        imgs = []
        raw_imgs = []

        # Only process creatures within our page range
        for i, avatar in enumerate(self.avatar_quests):
            if avatar.is_secret:
                continue

            avatar_quest = AvatarQuestTabFactory(avatar=avatar, user_id=self.user_id)
            avatar_quest_img = avatar_quest.generate_avatar_quest_tab_image()

            raw_imgs.append(avatar_quest_img)
            imgs.append(convert_to_png(avatar_quest_img, f'avatar_icon_{avatar.img_root}.png'))

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
        starting_index = (self.page_num_avatar_quests - 1) * tabs_per_page  # Adjust calculation to start from 0
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


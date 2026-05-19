from turtledemo.sorting_animate import ssort

from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import get_image_path, load_font
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.CreatureRarity import CreatureRarity, TRANSCENDANT
from src.discord.objects.TGOAvatar import TGOAvatar
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *
from src.resources.constants.general_constants import *


class AvatarQuestTabFactory:
    def __init__(self, avatar: TGOAvatar, user_id):
        self.avatar = avatar
        self.completed_quest_value = get_tgommo_db_handler().QueryHandler.execute_query(query=avatar.unlock_query, params=(user_id,))[0][0]
        self.is_completed = self.completed_quest_value >= self.avatar.unlock_threshold


    def generate_avatar_quest_tab_image(self):
        # Create a copy of the background to serve as the canvas
        base_img = Image.open(AVATAR_QUEST_TAB_WHITE_BORDER_IMAGE)
        self.place_progress_bar_on_image(base_img)

        if self.is_completed:
            completed_stamp_img = Image.open(AVATAR_QUEST_TAB_COMPLETE_TEXT_IMAGE)
            base_img.paste(completed_stamp_img, (0, 0), completed_stamp_img)
        else:
            self.add_text_to_image(image=base_img)

        base_img.paste(self.avatar.quest_icon_image, (0, 0), self.avatar.quest_icon_image)
        return base_img

    def place_progress_bar_on_image(self, base_image: Image):
        green_border_img = Image.open(AVATAR_QUEST_TAB_GREEN_BORDER_IMAGE)
        progress_indicator_img = Image.open(AVATAR_QUEST_TAB_PROGRESS_TAB_IMAGE)

        # slice progress bar based on completion
        width, height = green_border_img.size
        threshold = self.avatar.unlock_threshold or 0

        if threshold <= 0:
            progress_bar_width = 0
        else:
            fraction = self.completed_quest_value / threshold
            fraction = max(0.0, min(1.0, fraction))  # clamp between 0 and 1
            progress_bar_width = int(round(fraction * width))

        # crop the rightmost portion of the bar (filled area) and paste aligned to the right edge
        if progress_bar_width > 0:
            progress_bar_img = green_border_img.crop((width - progress_bar_width, 0, width, height))
            paste_x = width - progress_bar_width
            base_image.paste(progress_bar_img, (paste_x, 0), progress_bar_img)

        # place progress indicator centered on the fill edge (right-to-left), clamped to image bounds
        indicator_w, indicator_h = progress_indicator_img.size
        edge_x = width - progress_bar_width  # x coordinate of the fill edge
        indicator_x = edge_x - (indicator_w // 2)
        indicator_x = max(0, min(width - indicator_w, indicator_x))
        base_image.paste(progress_indicator_img, (indicator_x, 0), progress_indicator_img)
        return base_image

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)
        stats_num_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 20)

        # Draw the total catches
        text = f"{self.completed_quest_value} / {self.avatar.unlock_threshold}"

        draw.text((image.width - len(text)*7, (image.height // 2) + 2), text, fill=(0, 0, 0), font=stats_num_font, anchor="mm")
        return image

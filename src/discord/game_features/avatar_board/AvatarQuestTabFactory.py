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
        self.content_img_path = avatar.img_root
        self.completed_quest_value = get_tgommo_db_handler().QueryHandler.execute_query(query=avatar.unlock_query, params=(user_id,))[0][0]
        self.max_quest_value = avatar.unlock_threshold


    def generate_avatar_quest_tab_image(self):
        # Create a copy of the background to serve as the canvas
        base_img = Image.open(AVATAR_QUEST_TAB_WHITE_BORDER_IMAGE)
        quest_content_img = Image.open(f'{QUEST_TAB_INDIVIDUAL_QUEST_BASE}{self.content_img_path}{IMAGE_FILE_EXTENSION}')

        self.place_progress_bar_on_image(base_img)

        if self.completed_quest_value >= self.max_quest_value:
            completed_stamp_img = Image.open(AVATAR_QUEST_TAB_COMPLETE_TEXT_IMAGE)
            base_img.paste(completed_stamp_img, (0, 0), completed_stamp_img)
        else:
            self.add_text_to_image(image=base_img)

        base_img.paste(quest_content_img, (0, 0), quest_content_img)
        return base_img

    def place_progress_bar_on_image(self, base_image: Image.Image):
        green_border_img = Image.open(AVATAR_QUEST_TAB_GREEN_BORDER_IMAGE)
        progress_indicator_img = Image.open(AVATAR_QUEST_TAB_PROGRESS_TAB_IMAGE)

        # slice progress bar based on completion
        width, height = green_border_img.size
        progress_bar_width = width if self.completed_quest_value == 0 else (self.max_quest_value - self.completed_quest_value) * (width // self.max_quest_value)

        progress_bar_img = green_border_img.crop((progress_bar_width, 0, width, height))
        base_image.paste(progress_bar_img, (progress_bar_width, 0), progress_bar_img)

        # place progress indicator
        indicator_offset = (progress_bar_width - 18) if progress_bar_width > 18 else 0
        base_image.paste(progress_indicator_img, (indicator_offset, 0), progress_indicator_img)
        return base_image

    def add_text_to_image(self, image: Image.Image):
        draw = ImageDraw.Draw(image)
        stats_num_font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 20)

        # Draw the total catches
        text = f"{self.completed_quest_value} / {self.max_quest_value}"

        draw.text((image.width - len(text)*7, (image.height // 2) + 2), text, fill=(0, 0, 0), font=stats_num_font, anchor="mm")
        return image

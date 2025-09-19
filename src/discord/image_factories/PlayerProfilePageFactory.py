from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.testing.suite.test_reflection import users

from src.commons.CommonFunctions import center_text_on_pixel, resize_text_to_fit, add_border_to_image
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.image_factories.PlayerProfileSidePanelTabFactory import PlayerProfileSidePanelTabFactory
from src.discord.objects.CreatureRarity import MYTHICAL, get_rarity_by_name
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOPlayer import TGOPlayer
from src.resources.constants.TGO_MMO_constants import PLAYER_PROFILE_CREATURE_RESIZE_PERCENT, \
    PLAYER_PROFILE_CREATURE_COORDINATES, FONT_COLOR_WHITE
from src.resources.constants.file_paths import *


class PlayerProfilePageFactory:
    def __init__(self, user_id: int, tab_is_open: bool = False, open_tab: str = False):
        self.user_id = user_id

        self.player: TGOPlayer = None
        self.creature_team = []
        self._load_relevant_info()

        self.tab_is_open = tab_is_open
        self.open_tab = open_tab

        self.left_button_enabled = False
        self.right_button_enabled = False


    def _load_relevant_info(self):
        player_info = get_tgommo_db_handler().get_user_profile_by_user_id(self.user_id)
        self.player = TGOPlayer(player_id=player_info[0], user_id=player_info[1], nickname=player_info[2], avatar_id=player_info[3], background_id=player_info[4], creature_slot_id_1=player_info[5], creature_slot_id_2=player_info[6], creature_slot_id_3=player_info[7], creature_slot_id_4=player_info[8], creature_slot_id_5=player_info[9], creature_slot_id_6=player_info[10], currency=player_info[11], available_catches=player_info[12], rod_level=player_info[13], rod_amount=player_info[14], trap_level=player_info[15], trap_amount=player_info[16])

        creature_team_info = get_tgommo_db_handler().get_creatures_for_player_profile((self.player.creature_slot_id_1, self.player.creature_slot_id_2, self.player.creature_slot_id_3, self.player.creature_slot_id_4, self.player.creature_slot_id_5, self.player.creature_slot_id_6))
        for creature_info in creature_team_info:
            creature_name = creature_info[3] if creature_info[3] != '' else creature_info[2]
            rarity = MYTHICAL if creature_info[14] else get_rarity_by_name(creature_info[13])

            creature = TGOCreature(creature_id=creature_info[0],nickname=creature_info[1],name=creature_name,variant_name=creature_info[4],dex_no=creature_info[5],variant_no=creature_info[6],full_name=creature_info[7],scientific_name=creature_info[8],kingdom=creature_info[9],description=creature_info[10], img_root=creature_info[11], encounter_rate=creature_info[12], rarity = rarity,)

            self.creature_team.append(creature)


    def build_player_profile_page_image(self, new_page_number = None, is_verbose = None, show_variants = None, show_mythics = None):
        # set new values in case button was clicked
        player_profile_image = Image.open(f"{PLAYER_PROFILE_BACKGROUND_BASE}_{self.player.background_id}{IMAGE_FILE_EXTENSION}")
        dirt_patches_image = Image.open(PLAYER_PROFILE_DIRT_PATCHES_IMAGE)
        top_bar_image = Image.open(PLAYER_PROFILE_TOP_BAR_IMAGE)
        closed_panel_image = Image.open(PLAYER_PROFILE_SIDE_PANEL_CLOSED_IMAGE)

        # place layers on final image
        player_profile_image.paste(dirt_patches_image, (0, 0), dirt_patches_image)
        player_profile_image.paste(top_bar_image, (0, 0), top_bar_image)
        player_profile_image.paste(closed_panel_image, (0, 0), closed_panel_image)

        player_profile_image = self._place_avatar_on_image(player_profile_image=player_profile_image)
        player_profile_image = self._place_creatures_on_image(player_profile_img=player_profile_image)
        player_profile_image = self.place_username_on_image(player_profile_img=player_profile_image)

        player_profile_image = self.build_side_panel_content(player_profile_img=player_profile_image)

        return player_profile_image


    def _place_creatures_on_image(self, player_profile_img: Image.Image):
        for i in range(len(self.creature_team)):
            creature: TGOCreature = self.creature_team[i]

            creature_image = Image.open(f"{IMAGE_FOLDER_IMAGES_PATH}\\{creature.img_root}{'_S' if creature.rarity is MYTHICAL else ''}_THUMB{IMAGE_FILE_EXTENSION}")
            creature_image = creature_image.resize((int(creature_image.width * PLAYER_PROFILE_CREATURE_RESIZE_PERCENT), int(creature_image.height * PLAYER_PROFILE_CREATURE_RESIZE_PERCENT)), Image.LANCZOS)

            x_offset = PLAYER_PROFILE_CREATURE_COORDINATES[i][0] - (creature_image.width // 2)
            y_offset = PLAYER_PROFILE_CREATURE_COORDINATES[i][1] - (creature_image.height // 2)

            player_profile_img.paste(creature_image, (x_offset, y_offset), creature_image)

        return player_profile_img

    def _place_avatar_on_image(self, player_profile_image: Image.Image):
        player_avatar_image = Image.open(f"{PLAYER_PROFILE_AVATAR_BASE}_{self.player.avatar_id}{IMAGE_FILE_EXTENSION}")
        player_profile_image.paste(player_avatar_image, (0, 0), player_avatar_image)
        return player_profile_image

    def place_username_on_image(self, player_profile_img: Image.Image):
        draw = ImageDraw.Draw(player_profile_img)

        font = ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 50)
        font = resize_text_to_fit(text=self.player.nickname, draw=draw, font=font, max_width=300, min_font_size=10)

        # Get text dimensions
        text_bbox = draw.textbbox((0, 0), self.player.nickname, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Create a separate image for the text with border
        text_img = Image.new('RGBA', (text_width + 8, text_height + 8), (0, 0, 0, 0))
        x_offset, y_offset = 11, 10
        border_size = 4
        username_font_image = add_border_to_image(base_image=text_img, text=self.player.nickname, font=font, border_size=border_size, border_color=(0, 104, 145), font_color=FONT_COLOR_WHITE)

        # Paste the text image onto the profile image
        player_profile_img.paste(username_font_image, (x_offset - border_size, y_offset - border_size), username_font_image)

        # draw.text((11, 10), self.player.nickname, font=font, fill=FONT_COLOR_WHITE)

        return player_profile_img


    # side panel functions
    def build_side_panel_content(self, player_profile_img: Image.Image):
        side_drawer_border_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_OPEN_BORDER_IMAGE}")
        side_drawer_background_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_OPEN_BORDER_BACKGROUND_IMAGE}")

        if self.open_tab == "Team":
            side_drawer_background_image = self._build_team_tab(side_drawer_background_image)

            side_drawer_team_overlay = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_TEAM_OVERLAY_IMAGE}")
            side_drawer_background_image.paste(side_drawer_team_overlay, (0, 0), side_drawer_team_overlay)
        elif self.open_tab == "Collections":
            side_drawer_background_image = self._build_collections_tab(side_drawer_background_image)

            side_drawer_team_overlay = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_COLLECTIONS_OVERLAY_IMAGE}")
            side_drawer_background_image.paste(side_drawer_team_overlay, (0, 0), side_drawer_team_overlay)
        elif self.open_tab == "Environments":
            side_drawer_background_image = self._build_environments_tab(side_drawer_background_image)

            side_drawer_team_overlay = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_BIOMES_OVERLAY_IMAGE}")
            side_drawer_background_image.paste(side_drawer_team_overlay, (0, 0), side_drawer_team_overlay)

        left_button_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_LEFT_BUTTON_IMAGE if self.left_button_enabled else PLAYER_PROFILE_SIDE_PANEL_LEFT_BUTTON_DISABLED_IMAGE}")
        right_button_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_RIGHT_BUTTON_IMAGE if self.left_button_enabled else PLAYER_PROFILE_SIDE_PANEL_RIGHT_BUTTON_DISABLED_IMAGE}")

        side_drawer_background_image.paste(left_button_image, (0, 0), left_button_image)
        side_drawer_background_image.paste(right_button_image, (0, 0), right_button_image)

        player_profile_img.paste(side_drawer_background_image, (0, 0), side_drawer_background_image)
        player_profile_img.paste(side_drawer_border_image, (0, 0), side_drawer_border_image)

        return player_profile_img


    def _build_team_tab(self, background_img: Image.Image = None):
        current_offset = (1097,70)

        for i in range(len(self.creature_team)):
            creature: TGOCreature = self.creature_team[i]

            title = creature.nickname if creature.nickname != "" else creature.name
            creature_img_path = DEX_ICON_CREATURE_BASE + f"_{creature.img_root}" + f"{"_S" if creature.rarity == MYTHICAL else ""}" + IMAGE_FILE_EXTENSION
            image_color_path = f'{PLAYER_PROFILE_SIDE_PANEL_TABS_BACKGROUND_IMAGE_BASE}_{creature.rarity.name}{IMAGE_FILE_EXTENSION}'

            team_tab = PlayerProfileSidePanelTabFactory(tab_type="Team", player=self.player, content_image_path=creature_img_path, background_image_path=None,image_color_path=image_color_path, tab_title=title,tab_subtitle=creature.full_name, tab_footer='')
            team_tab_image = team_tab.create_tab()

            background_img.paste(team_tab_image, current_offset, team_tab_image)
            current_offset = (current_offset[0], current_offset[1] + team_tab_image.height + 17)

        return background_img

    def _build_collections_tab(self, player_: Image.Image):
        current_offset = (1097,70)

        content_image_path = ""
        background_image_path = ""
        image_color_path = ""
        tab_title = ""
        tab_subtitle = ""
        tab_footer = ""

        collections_tab = PlayerProfileSidePanelTabFactory(tab_type="Collections", player=self.player,content_image_path=content_image_path,background_image_path=background_image_path,image_color_path=image_color_path, tab_title=tab_title,tab_subtitle=tab_subtitle, tab_footer=tab_footer)

        return collections_tab

    def _build_environments_tab(self, player_profile_img: Image.Image):
        content_image_path=""
        background_image_path = ""
        image_color_path = ""
        tab_title = ""
        tab_subtitle = ""
        tab_footer = ""

        environments_tab = PlayerProfileSidePanelTabFactory(tab_type="Environments", player=self.player, content_image_path=content_image_path, background_image_path=background_image_path, image_color_path=image_color_path, tab_title=tab_title, tab_subtitle=tab_subtitle, tab_footer=tab_footer)

        return player_profile_img

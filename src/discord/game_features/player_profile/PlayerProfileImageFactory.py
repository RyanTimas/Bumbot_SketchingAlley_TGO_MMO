from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.player_profile.PlayerProfileSidePanelTabFactory import PlayerProfileSidePanelTabFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import PLAYER_PROFILE_CREATURE_RESIZE_PERCENT, \
    PLAYER_PROFILE_CREATURE_COORDINATES, FONT_COLOR_WHITE, TGOMMO_RARITY_MYTHICAL
from src.resources.constants.file_paths import *

PLAYER_PROFILE_TAB_OPEN_TEAM = "Team"
PLAYER_PROFILE_TAB_OPEN_COLLECTIONS = "Collections"
PLAYER_PROFILE_TAB_CLOSED = "Closed"

class PlayerProfileImageFactory(BaseImageFactory):
    def __init__(self, message_author, target_user, tab_is_open: bool = False, open_tab: str = None):
        super().__init__(message_author, target_user)
        self.open_tab = open_tab
        self.left_button_enabled = False
        self.right_button_enabled = False


    def reload_image(self, open_tab = None):
        # update components
        self.open_tab = open_tab if open_tab else self.open_tab
        return super().reload_image()

    def build_image(self):
        # set new values in case button was clicked
        player_profile_image = Image.open(f"{PLAYER_PROFILE_BACKGROUND_BASE}_{self.message_author.background_id}{IMAGE_FILE_EXTENSION}")
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

        if self.open_tab and self.open_tab != PLAYER_PROFILE_TAB_CLOSED:
            player_profile_image = self.build_side_panel_content(player_profile_img=player_profile_image)

        return player_profile_image

    def _place_creatures_on_image(self, player_profile_img: Image):
        for index, creature in enumerate(self.target_user.display_creatures):
            if creature.catch_id != -1:
                creature_image = creature.creature_image.resize((int(creature.creature_image.width * PLAYER_PROFILE_CREATURE_RESIZE_PERCENT), int(creature.creature_image.height * PLAYER_PROFILE_CREATURE_RESIZE_PERCENT)), Image.LANCZOS)

                x_offset = PLAYER_PROFILE_CREATURE_COORDINATES[index][0] - (creature_image.width // 2)
                y_offset = PLAYER_PROFILE_CREATURE_COORDINATES[index][1] - (creature_image.height // 2)

                player_profile_img.paste(creature_image, (x_offset, y_offset), creature_image)
        return player_profile_img
    def _place_avatar_on_image(self, player_profile_image: Image):
        player_avatar_image = Image.open(f"{PLAYER_PROFILE_AVATAR_BASE}_{self.target_user.avatar.avatar_type}_{self.target_user.avatar.img_root}{IMAGE_FILE_EXTENSION}")
        player_profile_image.paste(player_avatar_image, (0, 0), player_avatar_image)
        return player_profile_image
    def place_username_on_image(self, player_profile_img: Image):
        draw = ImageDraw.Draw(player_profile_img)
        font = resize_text_to_fit(text=self.target_user.nickname, draw=draw, font=ImageFont.truetype(FONT_FOREST_BOLD_FILE_TEMP, 50), max_width=300, min_font_size=10)

        # Get text dimensions
        text_bbox = draw.textbbox((0, 0), self.target_user.nickname, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Create a separate image for the text with border
        text_img = Image.new('RGBA', (text_width + 8, text_height + 8), (0, 0, 0, 0))
        x_offset, y_offset = 11, 10
        border_size = 4
        username_font_image = add_border_to_image(base_image=text_img, text=self.target_user.nickname, font=font, border_size=border_size, border_color=(0, 104, 145), font_color=FONT_COLOR_WHITE)

        # Paste the text image onto the profile image
        player_profile_img.paste(username_font_image, (x_offset - border_size, y_offset - border_size), username_font_image)
        return player_profile_img


    # side panel functions
    def build_side_panel_content(self, player_profile_img: Image):
        # define in memory images
        side_drawer_border_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_OPEN_BORDER_IMAGE}")
        side_drawer_team_overlay = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_TEAM_OVERLAY_IMAGE if self.open_tab == PLAYER_PROFILE_TAB_OPEN_TEAM else PLAYER_PROFILE_SIDE_PANEL_COLLECTIONS_OVERLAY_IMAGE}")
        side_drawer_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_OPEN_BORDER_BACKGROUND_IMAGE}")
        left_button_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_LEFT_BUTTON_IMAGE if self.left_button_enabled else PLAYER_PROFILE_SIDE_PANEL_LEFT_BUTTON_DISABLED_IMAGE}")
        right_button_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_RIGHT_BUTTON_IMAGE if self.left_button_enabled else PLAYER_PROFILE_SIDE_PANEL_RIGHT_BUTTON_DISABLED_IMAGE}")

        # build side drawer content
        side_drawer_image = self._build_team_tab(side_drawer_image) if self.open_tab == PLAYER_PROFILE_TAB_OPEN_TEAM else self._build_collections_tab(side_drawer_image)
        side_drawer_image.paste(side_drawer_team_overlay, (0, 0), side_drawer_team_overlay)

        # add button images
        side_drawer_image.paste(left_button_image, (0, 0), left_button_image)
        side_drawer_image.paste(right_button_image, (0, 0), right_button_image)

        # paste side drawer content
        player_profile_img.paste(side_drawer_image, (0, 0), side_drawer_image)
        player_profile_img.paste(side_drawer_border_image, (0, 0), side_drawer_border_image)

        return player_profile_img

    def _build_team_tab(self, background_img: Image):
        current_offset = (1097,70)

        for index, creature in enumerate(self.target_user.display_creatures):
            if creature.catch_id != -1:
                title = creature.nickname if creature.nickname != "" else creature.name
                image_color_path = f'{PLAYER_PROFILE_SIDE_PANEL_TABS_BACKGROUND_IMAGE_BASE}_{creature.local_rarity.name}{IMAGE_FILE_EXTENSION}'
                catch_date = convert_date_format_to_month_name(creature.caught_date)

                team_tab = PlayerProfileSidePanelTabFactory(tab_type=PLAYER_PROFILE_TAB_OPEN_TEAM, player=self.message_author, tab_image=creature.dex_icon_image, background_image_path=None, image_color_path=image_color_path, tab_title=title, tab_subtitle=creature.full_name, tab_footer=catch_date)
                team_tab_image = team_tab.create_tab()

                background_img.paste(team_tab_image, current_offset, team_tab_image)
                current_offset = (current_offset[0], current_offset[1] + team_tab_image.height + 17)
        return background_img
    def _build_collections_tab(self, background_img: Image):
        current_offset = (1097,70)

        active_collections = get_tgommo_db_handler().get_active_collections(convert_to_object=True)

        for collection in active_collections:
            collection.img_path = f'{DEX_ICON_CREATURE_BASE}_{collection.img_path}{IMAGE_FILE_EXTENSION}'
            collection.background_color_path = f'{PLAYER_PROFILE_SIDE_PANEL_TABS_BACKGROUND_IMAGE_BASE}_{collection.background_color_path}{IMAGE_FILE_EXTENSION}'

            remove_variants_suffix = f' c.variant_no=1;'

            caught_query = collection.caught_count_query[:-1] + f"{get_query_connector(collection.caught_count_query)}{remove_variants_suffix}" if 'variant_no' not in collection.caught_count_query else collection.caught_count_query
            total_query = collection.total_count_query[:-1] + f"{get_query_connector(collection.total_count_query)}{remove_variants_suffix}" if 'variant_no' not in collection.total_count_query else collection.total_count_query

            caught_number = get_tgommo_db_handler().execute_query(caught_query, params=(self.message_author.user_id,))[0][0]
            total_number = get_tgommo_db_handler().execute_query(total_query, params=())[0][0]
            subtitle = f"{caught_number}/{total_number}"

            collections_tab = PlayerProfileSidePanelTabFactory(tab_type=PLAYER_PROFILE_TAB_OPEN_COLLECTIONS, player=self.message_author, collection=collection, tab_image=Image.open(collection.img_path), background_image_path=None, image_color_path=collection.background_color_path, tab_title=collection.title, tab_subtitle=subtitle, tab_footer="todo")
            collections_tab_image = collections_tab.create_tab()

            background_img.paste(collections_tab_image, current_offset, collections_tab_image)
            current_offset = (current_offset[0], current_offset[1] + collections_tab_image.height + 17)

        return background_img


async def build_text_based_user_creature_collection(author, ctx):
    creature_collection = get_tgommo_db_handler().get_user_creatures_by_user_id(author.id, )

    page_num = 0
    pages = [f"Total Unique Creatures Caught: {len(creature_collection)}"]

    # add an entry for each creature in collection
    for creature_index, creature in enumerate(creature_collection):
        current_page = pages[page_num]

        is_mythical = creature.local_rarity.name == TGOMMO_RARITY_MYTHICAL
        nickname = f'**__{creature.nickname}❗__**' if creature.nickname != '' else creature.name + ('✨' if is_mythical else '')

        newlines = f'{'\n' if creature.creature_id != creature_collection[creature_index - 1].catch_id else ''}\n'
        new_entry = f"{newlines}{creature_index + 1}.  \t\t [{creature.catch_id}] \t ({pad_text(creature.name, 20)}) \t {pad_text(nickname, 20)}"

        if len(current_page) + len(new_entry) > 1900:
            page_num += 1
            pages.append('')

        pages[page_num] += new_entry

    # create page images for user to see
    for page_index, page in enumerate(pages):
        text = "\n".join([f"# {author.name}'s Creature Collection ({page_index + 1}/{len(pages)}):",])
        text += f'{page}'
        await ctx.message.reply(text)


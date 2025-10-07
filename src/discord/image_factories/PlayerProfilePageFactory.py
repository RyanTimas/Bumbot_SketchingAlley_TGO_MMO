from PIL import Image, ImageDraw, ImageFont

from src.commons.CommonFunctions import resize_text_to_fit, add_border_to_image, pad_text
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.image_factories.PlayerProfileSidePanelTabFactory import PlayerProfileSidePanelTabFactory
from src.discord.objects.CreatureRarity import MYTHICAL, get_rarity_by_name
from src.discord.objects.TGOCreature import TGOCreature
from src.discord.objects.TGOPlayer import TGOPlayer
from src.resources.constants.TGO_MMO_constants import PLAYER_PROFILE_CREATURE_RESIZE_PERCENT, \
    PLAYER_PROFILE_CREATURE_COORDINATES, FONT_COLOR_WHITE
from src.resources.constants.file_paths import *

TEAM = "Team"
COLLECTIONS = "Collections"
ENVIRONMENTS = "Environments"

class PlayerProfilePageFactory:
    def __init__(self, user_id, target_user, tab_is_open: bool = False, open_tab: str = TEAM):
        self.user_id = user_id
        self.target_user = target_user

        self.player: TGOPlayer = None
        self.creature_team = []
        self.load_player_info()

        self.tab_is_open = tab_is_open
        self.open_tab = open_tab

        self.left_button_enabled = False
        self.right_button_enabled = False


    def load_player_info(self):
        player_info = get_tgommo_db_handler().insert_new_user_profile(user_id=self.target_user.id, nickname=self.target_user.name)

        self.player = TGOPlayer(player_id=player_info[0], user_id=player_info[1], nickname=player_info[2], avatar_id=player_info[3], background_id=player_info[4], creature_slot_id_1=player_info[5], creature_slot_id_2=player_info[6], creature_slot_id_3=player_info[7], creature_slot_id_4=player_info[8], creature_slot_id_5=player_info[9], creature_slot_id_6=player_info[10], currency=player_info[11], available_catches=player_info[12], rod_level=player_info[13], rod_amount=player_info[14], trap_level=player_info[15], trap_amount=player_info[16])

        self.creature_team = []
        creature_team_info = get_tgommo_db_handler().get_creatures_for_player_profile((self.player.creature_slot_id_1, self.player.creature_slot_id_2, self.player.creature_slot_id_3, self.player.creature_slot_id_4, self.player.creature_slot_id_5, self.player.creature_slot_id_6))
        for creature_info in creature_team_info:
            creature_name = creature_info[3] if creature_info[3] != '' else creature_info[2]
            rarity = MYTHICAL if creature_info[14] else get_rarity_by_name(creature_info[13])

            creature = TGOCreature(creature_id=creature_info[0],nickname=creature_info[1],name=creature_name,variant_name=creature_info[4],dex_no=creature_info[5],variant_no=creature_info[6],full_name=creature_info[7],scientific_name=creature_info[8],kingdom=creature_info[9],description=creature_info[10], img_root=creature_info[11], encounter_rate=creature_info[12], rarity = rarity,)

            self.creature_team.append(creature)


    def build_player_profile_page_image(self, new_page_number = None, tab_is_open = None, open_tab = None):
        # self.new_page_number = self.new_page_number if new_page_number is None else new_page_number
        self.tab_is_open = self.tab_is_open if tab_is_open is None else tab_is_open
        self.open_tab = self.open_tab if open_tab is None else open_tab

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

        if self.tab_is_open:
            player_profile_image = self.build_side_panel_content(player_profile_img=player_profile_image)

        return player_profile_image


    def _place_creatures_on_image(self, player_profile_img: Image.Image):
        for i in range(len(self.creature_team)):
            creature: TGOCreature = self.creature_team[i]

            creature_image = Image.open(f"{IMAGE_FOLDER_CREATURES_PATH}\\{creature.img_root}{'_S' if creature.rarity is MYTHICAL else ''}_THUMB{IMAGE_FILE_EXTENSION}")
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

        if self.open_tab == TEAM:
            side_drawer_background_image = self._build_team_tab(side_drawer_background_image)

            side_drawer_team_overlay = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_TEAM_OVERLAY_IMAGE}")
            side_drawer_background_image.paste(side_drawer_team_overlay, (0, 0), side_drawer_team_overlay)
        elif self.open_tab == COLLECTIONS:
            side_drawer_background_image = self.build_collections_tab(side_drawer_background_image)

            side_drawer_team_overlay = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_COLLECTIONS_OVERLAY_IMAGE}")
            side_drawer_background_image.paste(side_drawer_team_overlay, (0, 0), side_drawer_team_overlay)
        elif self.open_tab == ENVIRONMENTS:
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


    def _build_team_tab(self, background_img: Image.Image):
        current_offset = (1097,70)

        for i in range(len(self.creature_team)):
            creature: TGOCreature = self.creature_team[i]

            title = creature.nickname if creature.nickname != "" else creature.name
            creature_img_path = DEX_ICON_CREATURE_BASE + f"_{creature.img_root}" + f"{"_S" if creature.rarity == MYTHICAL else ""}" + IMAGE_FILE_EXTENSION
            image_color_path = f'{PLAYER_PROFILE_SIDE_PANEL_TABS_BACKGROUND_IMAGE_BASE}_{creature.rarity.name}{IMAGE_FILE_EXTENSION}'

            team_tab = PlayerProfileSidePanelTabFactory(tab_type=TEAM, player=self.player, content_image_path=creature_img_path, background_image_path=None,image_color_path=image_color_path, tab_title=title,tab_subtitle=creature.full_name, tab_footer='')
            team_tab_image = team_tab.create_tab()

            background_img.paste(team_tab_image, current_offset, team_tab_image)
            current_offset = (current_offset[0], current_offset[1] + team_tab_image.height + 17)

        return background_img

    def build_collections_tab(self, background_img: Image.Image):
        current_offset = (1097,70)

        active_collections = get_tgommo_db_handler().get_active_collections(convert_to_object=True)

        for collection in active_collections:
            collection.image_path = f'{DEX_ICON_CREATURE_BASE}_{collection.image_path}{IMAGE_FILE_EXTENSION}'
            collection.background_color_path = f'{PLAYER_PROFILE_SIDE_PANEL_TABS_BACKGROUND_IMAGE_BASE}_{collection.background_color_path}{IMAGE_FILE_EXTENSION}'

            caught_number = get_tgommo_db_handler().execute_query(collection.caught_count_query, params=(self.player.user_id,))[0][0]
            total_number = get_tgommo_db_handler().execute_query(collection.total_count_query, params=())[0][0]
            subtitle = f"{caught_number}/{total_number}"

            collections_tab = PlayerProfileSidePanelTabFactory(tab_type=COLLECTIONS, player=self.player,content_image_path=collection.image_path,background_image_path=None,image_color_path=collection.background_color_path, tab_title=collection.title,tab_subtitle=subtitle, tab_footer="todo")
            collections_tab_image = collections_tab.create_tab()

            if caught_number == total_number:
                first_star_image = Image.open(f"{PLAYER_PROFILE_SIDE_PANEL_TABS_STARS_IMAGE_BASE}_1{IMAGE_FILE_EXTENSION}")
                collections_tab_image.paste(first_star_image, (0, 0), first_star_image)

            background_img.paste(collections_tab_image, current_offset, collections_tab_image)
            current_offset = (current_offset[0], current_offset[1] + collections_tab_image.height + 17)

        return background_img


    def _build_environments_tab(self, player_profile_img: Image.Image):
        content_image_path=""
        background_image_path = ""
        image_color_path = ""
        tab_title = ""
        tab_subtitle = ""
        tab_footer = ""

        environments_tab = PlayerProfileSidePanelTabFactory(tab_type="Environments", player=self.player, content_image_path=content_image_path, background_image_path=background_image_path, image_color_path=image_color_path, tab_title=tab_title, tab_subtitle=tab_subtitle, tab_footer=tab_footer)

        return player_profile_img


async def build_user_creature_collection(author, ctx):
    creature_collection = get_tgommo_db_handler().get_creature_collection_by_user(author.id)

    page_num = 0
    pages = [f"Total Unique Creatures Caught: {len(creature_collection)}"]

    # add an entry for each creature in collection
    for creature_index, creature in enumerate(creature_collection):
        current_page = pages[page_num]

        catch_id = creature[0]
        creature_id = creature[1]
        creature_name = f'{creature[2]}{f' -  {creature[3]}' if creature[3] != '' else ''}'
        spawn_rarity = creature[5]
        is_mythical = creature[6]
        nickname = f'**__{creature[4]}❗__**' if creature[4] != '' else creature[2] + ('✨' if is_mythical else '')

        newlines = f'{'\n' if creature_id != creature_collection[creature_index - 1][1] else ''}\n'
        new_entry = f"{newlines}{creature_index + 1}.  \t\t [{catch_id}] \t ({pad_text(creature_name, 20)}) \t {pad_text(nickname, 20)}"

        if len(current_page) + len(new_entry) > 1900:
            page_num += 1
            pages.append('')

        pages[page_num] += new_entry

    # create page images for user to see
    for page_index, page in enumerate(pages):
        text = "\n".join([
            f"# {author.name}'s Creature Collection ({page_index + 1}/{len(pages)}):",
        ])

        text += f'{page}'
        await ctx.message.reply(text)
    # await ctx.response.send_message("Someone else already caught this creature...", ephemeral=True)


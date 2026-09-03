from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.omnipotent_bait_manager.OmnipotentBaitManagerCreatureCellImageFactory import \
    OmnipotentBaitManagerCreatureCellImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class OmnipotentBaitManagerImageFactory(BaseImageFactory):
    def __init__(self, message_author, active_environment=None):
        super().__init__(message_author=message_author, target_user=message_author)

        self.max_icons_per_page = 21

        self.active_environment = active_environment
        self.environment_icons = self.get_environment_icons()

        self.creatures = self.get_creatures_for_environment()
        self.creature_icons = self.get_creature_grid_icons(creatures=self.creatures, active_environment=self.active_environment)
        self.environment_icons = self.get_environment_icons()

        self.load_relevant_info()

    def reload_image(self, target_user=None, new_page_number=None, open_tab=None, active_environment=None):
        self.load_relevant_info(target_user= target_user, new_page_number=new_page_number, open_tab=open_tab, active_environment=active_environment)
        return self.build_image()
    def load_relevant_info(self, target_user=None, new_page_number=None, open_tab=None, active_environment=None):
        self.target_user = target_user if target_user else self.target_user
        self.page_num = new_page_number if new_page_number else self.page_num
        self.open_tab = open_tab if open_tab else self.open_tab

        if active_environment:
            self.active_environment = active_environment
            self.creatures = self.get_creatures_for_environment()
            self.creature_icons = self.get_creature_grid_icons(creatures=self.creatures, active_environment=self.active_environment)
            self.environment_icons = self.get_environment_icons()

    def build_image(self):
        omnipotentbait_manager_image = Image.open(OMNIPOTENT_BAIT_MANAGER_BG_IMAGE)

        creature_grid = self.build_grid(icons=self.creature_icons, grid_size=(1746, 662), icon_size=(246, 218), icons_per_page=21, icons_per_row=7, horizontal_padding=4, vertical_padding=4)
        omnipotentbait_manager_image.paste(creature_grid, get_centered_image_position(foreground_image=creature_grid, background_image=omnipotentbait_manager_image, center_pixel=(960, 674)), creature_grid)

        environment_grid = self.build_grid(icons=self.environment_icons, grid_size=(1746, 218), icon_size=(246, 218), icons_per_page=len(self.environment_icons), icons_per_row=len(self.environment_icons), horizontal_padding=4, vertical_padding=4, use_page_number=False)
        environment_grid = crop_to_content(image=environment_grid, padding=0)

        omnipotentbait_manager_image.paste(environment_grid, get_centered_image_position(foreground_image=environment_grid, background_image=omnipotentbait_manager_image, center_pixel=(1280, 165)), environment_grid)

        return self.add_text_to_image(image = omnipotentbait_manager_image)

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        # ADD creature count to image
        displayed_creatures_count_text = f"showing {((self.page_num - 1) * self.max_icons_per_page) +1} - {min((self.page_num - 1) * self.max_icons_per_page + self.max_icons_per_page, len(self.creatures))} of {len(self.creatures)} creatures"
        font = resize_text_to_fit(text=displayed_creatures_count_text, draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 20), max_width=396, min_font_size=14)

        draw.text( get_centered_text_position(text=displayed_creatures_count_text, font=font, center_pixel_location=(960, 1038)), displayed_creatures_count_text, fill=FONT_COLOR_OMNIPOTENT_BAIT_MANAGER_BEIGE, font=font)

        return image

    '''---- SUPPORT FUNCTIONS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def get_creatures_for_environment(self):
        # Fetch creatures for the active environment (use environment_id so variants are respected)
        creatures = get_tgommo_db_handler().get_creatures_for_environment_by_dex_no(dex_no=self.active_environment.dex_no, exclude_duplicates=True)
        self.total_pages = (len(creatures) + self.max_icons_per_page - 1) // self.max_icons_per_page  # Calculate total pages

        # todo - these return an int, need the list of creatures
        # user_caught_creatures_in_environment = {c.creature_id for c in get_tgommo_db_handler().get_total_unique_creatures_caught_by_user_and_environment_dex_no(user_id=self.target_user.user_id, environment_dex_no=self.active_environment.dex_no)}
        # user_caught_creatures_in_other_environments = {c.creature_id for c in get_tgommo_db_handler().get_total_unique_creatures_caught_by_user(user_id=self.target_user.user_id)}
        # server_caught_creatures = {c.creature_id for c in get_tgommo_db_handler().get_total_unique_creatures_caught_by_server()}

        # Assign caught_type using fast set membership checks
        for creature in creatures:
            # if creature.creature_id in user_caught_creatures_in_environment:
            #     creature.caught_type = OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_CAUGHT
            # elif creature.creature_id in user_caught_creatures_in_other_environments:
            #     creature.caught_type = OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_ENVIRONMENT
            # elif creature.creature_id in server_caught_creatures:
            #     creature.caught_type = OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_SERVER
            # else:
            #     creature.caught_type = OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT
            creature.caught_type = random.choice(seq=[OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_CAUGHT, OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_ENVIRONMENT, OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_SERVER, OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT])
        return creatures

    def get_creature_grid_icons(self, creatures, active_environment):
        grid_icons = []
        for creature in creatures:
            creature_cell_image_factory = OmnipotentBaitManagerCreatureCellImageFactory(creature=creature, active_environment=active_environment)
            creature_cell_image = creature_cell_image_factory.generate_creature_cell_image()
            grid_icons.append(creature_cell_image)
        return grid_icons

    def get_environment_icons(self):
        environment_icons = []
        for environment in get_tgommo_db_handler().get_all_environments_in_rotation():
            environment_icon_image = Image.open(f"{OMNIPOTENT_BAIT_MANAGER_ENVIRONMENT_ICON_BASE}{environment.local_img_suffix}{IMAGE_FILE_EXTENSION}")
            if environment.dex_no != self.active_environment.dex_no:
                environment_icon_image = set_image_opacity(image=environment_icon_image, opacity=0.8)
            environment_icons.append(environment_icon_image)
        return environment_icons

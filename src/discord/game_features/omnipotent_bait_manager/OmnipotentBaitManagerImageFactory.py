from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.omnipotent_bait_manager.OmnipotentBaitManagerCreatureCellImageFactory import \
    OmnipotentBaitManagerCreatureCellImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


class OmnipotentBaitManagerImageFactory(BaseImageFactory):
    def __init__(self, message_author, active_environment=None):
        super().__init__(message_author=message_author, target_user=message_author)

        self.max_icons_per_page = 21

        self.active_environment = active_environment
        # Caches to avoid rebuilding images repeatedly
        self._creature_icon_cache = {}  # key: (creature_id, caught_type, environment_dex_no) -> PIL.Image
        self._environment_icon_cache = {}  # key: (environment_dex_no, is_active) -> PIL.Image

        # Preload environment icons once
        self.environment_icons = self.get_environment_icons()

        self.creatures = self.get_creatures_for_environment()
        # Do NOT build all creature icons up-front. Build only those required for the current page in build_image.
        self.creature_icons = []

        # Preload commonly used font to avoid repeated loading
        self._small_font = ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 20)

        self.load_relevant_info()

    def reload_image(self, target_user=None, new_page_number=None, open_tab=None, active_environment=None):
        self.load_relevant_info(target_user= target_user, new_page_number=new_page_number, open_tab=open_tab, active_environment=active_environment)
        return self.build_image()
    def load_relevant_info(self, target_user=None, new_page_number=None, open_tab=None, active_environment=None):
        self.target_user = target_user if target_user else self.target_user
        self.page_num = new_page_number if new_page_number else self.page_num
        self.open_tab = open_tab if open_tab else self.open_tab

        if active_environment:
            # If environment changed, update and clear caches that depend on environment
            if not self.active_environment or active_environment.dex_no != self.active_environment.dex_no:
                self.active_environment = active_environment
                self.creatures = self.get_creatures_for_environment()

                # todo: move this to logic to base image factory
                try:
                    self.page_num = min(self.page_num, self.total_pages)
                except Exception:
                    self.page_num = 1

                self.creature_icons = []
                # environment icons depend on which environment is active (for opacity), clear/cache will rebuild as needed
                self._environment_icon_cache.clear()
                # Creature icons depend on environment; clear cache
                self._creature_icon_cache.clear()
                self.environment_icons = self.get_environment_icons()

    def build_image(self):
        omnipotentbait_manager_image = Image.open(OMNIPOTENT_BAIT_MANAGER_BG_IMAGE)

        # Only build icons for the currently visible page to save time/memory
        start_idx = (self.page_num - 1) * self.max_icons_per_page
        end_idx = start_idx + self.max_icons_per_page
        self.creature_icons = self.get_creature_grid_icons(creatures=self.creatures[start_idx:end_idx], active_environment=self.active_environment)

        # We already sliced the icons for the current page, so prevent build_grid from re-paginating
        creature_grid = self.build_grid(icons=self.creature_icons, grid_size=(1746, 662), icon_size=(246, 218), icons_per_page=self.max_icons_per_page, icons_per_row=7, horizontal_padding=4, vertical_padding=4, use_page_number=False)
        omnipotentbait_manager_image.paste(creature_grid, get_centered_image_position(foreground_image=creature_grid, background_image=omnipotentbait_manager_image, center_pixel=(960, 674)), creature_grid)

        environment_grid = self.build_grid(icons=self.environment_icons, grid_size=(1746, 218), icon_size=(246, 218), icons_per_page=len(self.environment_icons), icons_per_row=len(self.environment_icons), horizontal_padding=4, vertical_padding=4, use_page_number=False)
        environment_grid = crop_to_content(image=environment_grid, padding=0)

        omnipotentbait_manager_image.paste(environment_grid, get_centered_image_position(foreground_image=environment_grid, background_image=omnipotentbait_manager_image, center_pixel=(1280, 165)), environment_grid)

        return self.add_text_to_image(image = omnipotentbait_manager_image)

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        # ADD creature count to image
        displayed_creatures_count_text = f"showing {((self.page_num - 1) * self.max_icons_per_page) +1} - {min((self.page_num - 1) * self.max_icons_per_page + self.max_icons_per_page, len(self.creatures))} of {len(self.creatures)} creatures"
        font = resize_text_to_fit(text=displayed_creatures_count_text, draw=draw, font=self._small_font, max_width=396, min_font_size=14)

        draw.text( get_centered_text_position(text=displayed_creatures_count_text, font=font, center_pixel_location=(960, 1038)), displayed_creatures_count_text, fill=FONT_COLOR_OMNIPOTENT_BAIT_MANAGER_BEIGE, font=font)

        return image

    '''---- SUPPORT FUNCTIONS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def get_creatures_for_environment(self):
        # Fetch creatures for the active environment (use environment_id so variants are respected)
        creatures = get_tgommo_db_handler().get_creatures_for_environment_by_dex_no(dex_no=self.active_environment.dex_no, exclude_duplicates=True)
        creatures.sort(key=lambda c: (c.local_dex_no, c.variant_no))
        self.total_pages = (len(creatures) + self.max_icons_per_page - 1) // self.max_icons_per_page  # Calculate total pages

        # Assign caught_type using fast set membership checks
        caught_creatures_by_user_in_environment, caught_creatures_by_user, caught_creatures_by_server_list = get_tgommo_db_handler().get_creature_id_lists_for_omnipotent_menu(user_id=self.target_user.user_id, environment_dex_no=self.active_environment.dex_no)
        for creature in creatures:
            if creature.creature_id in caught_creatures_by_user_in_environment:
                creature.caught_type = OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_CAUGHT
            elif creature.creature_id in caught_creatures_by_user:
                creature.caught_type = OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_ENVIRONMENT
            elif creature.creature_id in caught_creatures_by_server_list:
                creature.caught_type = OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_SERVER
            else:
                creature.caught_type = OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT
            creature.caught_type = random.choice(seq=[OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_CAUGHT, OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_ENVIRONMENT, OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_SERVER, OMNIPOTENT_BAIT_MANAGER_CREATURE_CATCH_TYPE_UNCAUGHT])
        return creatures

    # python
    def has_multiple_variants_for_dex(self, dex_no) -> bool:
        """
        Return True if `self.creatures` contains more than one creature with the given dex_no.
        Checks `local_dex_no` first, then `dex_no`. Accepts int or string input.
        """
        # todo: change this to a cached list of repeat dex numbers for speed if this is called frequently
        if not getattr(self, "creatures", None):
            return False

        # Try integer comparison first for speed/accuracy
        try:
            target = int(dex_no)

            def matches(c):
                return getattr(c, "local_dex_no", None) == target or getattr(c, "dex_no", None) == target
        except Exception:
            target = str(dex_no)

            def matches(c):
                return str(getattr(c, "local_dex_no", "")) == target or str(getattr(c, "dex_no", "")) == target

        count = 0
        for creature in self.creatures:
            if matches(creature):
                count += 1
                if count > 1:
                    return True
        return False

    def get_creature_grid_icons(self, creatures, active_environment):
        # Build creature icons in parallel for the visible page and cache results to avoid re-generation
        grid_icons = []

        def build_icon(creature):
            try:
                # Cache key depends on creature id, its caught_type (which affects appearance), and current environment
                key = (getattr(creature, 'creature_id', id(creature)), getattr(creature, 'caught_type', None),
                       getattr(active_environment, 'dex_no', None))
                cached = self._creature_icon_cache.get(key)
                if cached:
                    return cached.copy()

                factory = OmnipotentBaitManagerCreatureCellImageFactory(creature=creature, active_environment=active_environment)
                img = factory.generate_creature_cell_image()
                # store original in cache and return a copy to prevent external mutation side-effects
                try:
                    self._creature_icon_cache[key] = img.copy()
                    return img.copy()
                except Exception:
                    return img
            except Exception:
                # on unexpected failure return a fallback sequential generation result
                try:
                    return OmnipotentBaitManagerCreatureCellImageFactory(creature=creature, active_environment=active_environment).generate_creature_cell_image()
                except Exception:
                    return None  # caller can filter out Nones if necessary

        max_workers = min(8, (os.cpu_count() or 4))
        with ThreadPoolExecutor(max_workers=max_workers) as exe:
            # executor.map preserves the order of the input iterable
            for img in exe.map(build_icon, creatures):
                if img is not None:
                    grid_icons.append(img)

        return grid_icons

    def get_environment_icons(self):
        environment_icons = []
        for environment in get_tgommo_db_handler().get_all_environments_in_rotation():
            is_active = (environment.dex_no == self.active_environment.dex_no)
            key = (environment.dex_no, is_active)
            cached = self._environment_icon_cache.get(key)
            if cached:
                environment_icons.append(cached.copy())
                continue

            environment_icon_image = Image.open(f"{OMNIPOTENT_BAIT_MANAGER_ENVIRONMENT_ICON_BASE}{environment.local_img_suffix}{IMAGE_FILE_EXTENSION}")
            if not is_active:
                environment_icon_image = set_image_opacity(image=environment_icon_image, opacity=0.8)

            try:
                self._environment_icon_cache[key] = environment_icon_image.copy()
                environment_icons.append(environment_icon_image.copy())
            except Exception:
                environment_icons.append(environment_icon_image)

        return environment_icons

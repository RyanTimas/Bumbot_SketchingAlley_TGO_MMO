import discord

from src.commons.CommonFunctions import convert_to_png, interaction_guard
from src.discord.game_features.encyclopedia.EncyclopediaImageFactory import EncyclopediaImageFactory
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.TGO_MMO_constants import *

next_ = "next"
previous = "previous"
jump = "jump"

class EncyclopediaView(BaseView):
    def __init__(self, message_author, target_user, encyclopedia_image_factory: EncyclopediaImageFactory,original_view=None, original_image_files=[]):
        super().__init__(message_author=message_author, target_user=target_user, image_factory=encyclopedia_image_factory, original_view=original_view, original_view_files=original_image_files)

        # State variables for toggles
        self.is_verbose = None
        self.show_variants = None
        self.show_mythics = None

        self.time = None
        self.rarity = None
        self.creature_class = None

        self.is_xl_mode = False

        self.expanded_view_type =ENCYCLOPEDIA_BASE_EXPANDED_DISPLAY_KEY

        # basic filter buttons
        self.base_filter_expansion_button = self.create_expansion_button(ENCYCLOPEDIA_BASE_EXPANDED_DISPLAY_KEY, row=2)
        self.verbose_button = self.create_toggle_button(ENCYCLOPEDIA_VERBOSE_MODE, row=3)
        self.variants_button = self.create_toggle_button(ENCYCLOPEDIA_VARIANTS_DISPLAY_KEY, row=3)
        self.mythics_button = self.create_toggle_button(ENCYCLOPEDIA_MYTHICAL_DISPLAY_KEY, row=3)

        # deluxe filter options
        self.time_of_day_filter_expansion_button = self.create_expansion_button(ENCYCLOPEDIA_EXPANDED_TIME_DISPLAY_KEY, row=2)
        self.day_only_button = self.create_toggle_button(ENCYCLOPEDIA_DAY_SPAWNS_DISPLAY_KEY, row=3)
        self.night_only_button = self.create_toggle_button(ENCYCLOPEDIA_NIGHT_SPAWNS_DISPLAY_KEY, row=3)

        self.rarity_filter_expansion_button = self.create_expansion_button(ENCYCLOPEDIA_EXPANDED_RARITY_DISPLAY_KEY, row=2)
        self.rarity_dropdown = self.create_rarity_dropdown(row=3)

        self.class_filter_expansion_button = self.create_expansion_button(ENCYCLOPEDIA_EXPANDED_CLASS_DISPLAY_KEY, row=2)
        self.class_dropdown = self.create_class_dropdown(row=3)

        self.is_xl_button = self.create_toggle_button(ENCYCLOPEDIA_XL_MODE, row=4)

        # Add buttons to view
        self.refresh_view()

    # CREATE BUTTONS
    def create_toggle_button(self, button_type, row=1):
        data_options = {
            ENCYCLOPEDIA_VERBOSE_MODE: ["Show Detailed View", discord.ButtonStyle.green, None],
            ENCYCLOPEDIA_VARIANTS_DISPLAY_KEY: ["Show Variants", discord.ButtonStyle.green, None],
            ENCYCLOPEDIA_MYTHICAL_DISPLAY_KEY: ["Show Mythics", discord.ButtonStyle.green, "✨"],
            ENCYCLOPEDIA_NIGHT_SPAWNS_DISPLAY_KEY: ["Show Night Spawns", discord.ButtonStyle.green, "🌙"],
            ENCYCLOPEDIA_DAY_SPAWNS_DISPLAY_KEY: ["Show Day Spawns", discord.ButtonStyle.green, "☀️"],
            ENCYCLOPEDIA_XL_MODE: ["Show Full View", discord.ButtonStyle.green, "➕"]
        }
        data = data_options[button_type]
        button = discord.ui.Button(label=data[0], style=data[1], emoji=data[2], row=row)

        button.callback = self.toggle_callback(button_type)
        return button
    def toggle_callback(self, button_type):
        @interaction_guard(self)
        async def callback(interaction, defer_response=False):
            self.is_verbose = not self.is_verbose if button_type == ENCYCLOPEDIA_VERBOSE_MODE else self.is_verbose
            self.show_variants = not self.show_variants if button_type == ENCYCLOPEDIA_VARIANTS_DISPLAY_KEY else self.show_variants
            self.show_mythics = not self.show_mythics if button_type == ENCYCLOPEDIA_MYTHICAL_DISPLAY_KEY else self.show_mythics
            self.is_xl_mode = not self.is_xl_mode if button_type == ENCYCLOPEDIA_XL_MODE else self.is_xl_mode
            self.update_time_filter(button_type)

            reloaded_image = self.reload_image(is_verbose=self.is_verbose, show_variants=self.show_variants, show_mythics=self.show_mythics, time=self.time, is_xl_mode=self.is_xl_mode, rarity=self.rarity, creature_class=self.creature_class)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback

    def create_expansion_button(self, expansion_type, row=1):
        data_options = {
            ENCYCLOPEDIA_BASE_EXPANDED_DISPLAY_KEY: ["Basic Filters", discord.ButtonStyle.blurple],
            ENCYCLOPEDIA_EXPANDED_TIME_DISPLAY_KEY: ["🌗Time", discord.ButtonStyle.blurple],
            ENCYCLOPEDIA_EXPANDED_RARITY_DISPLAY_KEY: ["⭐Rarity", discord.ButtonStyle.blurple],
            ENCYCLOPEDIA_EXPANDED_CLASS_DISPLAY_KEY: ["🌿Class", discord.ButtonStyle.blurple],
        }
        data = data_options[expansion_type]
        button = discord.ui.Button(label=data[0], style=data[1], row=row)

        button.callback = self.expansion_callback(expansion_type)
        return button
    def expansion_callback(self, expansion_type):
        @interaction_guard(self)
        async def callback(interaction):
            self.expanded_view_type = expansion_type

            reloaded_image = self.reload_image(is_verbose=self.is_verbose, show_variants=self.show_variants, show_mythics=self.show_mythics, time=self.time, is_xl_mode=self.is_xl_mode, rarity=self.rarity, creature_class=self.creature_class)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback

    # CREATE DROPDOWNS
    def create_rarity_dropdown(self, row=3):
        options = [
            discord.SelectOption(label="All Rarities", value="None", description="Show all rarity levels"),
            discord.SelectOption(label=TGOMMO_RARITY_COMMON, value=TGOMMO_RARITY_COMMON),
            discord.SelectOption(label=TGOMMO_RARITY_UNCOMMON, value=TGOMMO_RARITY_UNCOMMON),
            discord.SelectOption(label=TGOMMO_RARITY_RARE, value=TGOMMO_RARITY_RARE),
            discord.SelectOption(label=TGOMMO_RARITY_EPIC, value=TGOMMO_RARITY_EPIC),
            discord.SelectOption(label=TGOMMO_RARITY_LEGENDARY, value=TGOMMO_RARITY_LEGENDARY),
            discord.SelectOption(label=TGOMMO_RARITY_TRANSCENDANT, value=TGOMMO_RARITY_TRANSCENDANT)
        ]

        dropdown = discord.ui.Select(placeholder=self.rarity if self.rarity else "Filter by rarity...", options=options, row=row)
        dropdown.callback = self.rarity_dropdown_callback()
        return dropdown
    def rarity_dropdown_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            selected_value = interaction.data['values'][0]
            self.rarity = selected_value

            reloaded_image = self.reload_image(is_verbose=self.is_verbose, show_variants=self.show_variants, show_mythics=self.show_mythics, time=self.time, is_xl_mode=self.is_xl_mode, rarity=self.rarity, creature_class=self.creature_class)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback

    def create_class_dropdown(self, row=3):
        options = [
            discord.SelectOption(label="All Creatures", value="None"),
            discord.SelectOption(label=MAMMAL, value=MAMMAL),
            discord.SelectOption(label=BIRD, value=BIRD),
            discord.SelectOption(label=REPTILE, value=REPTILE),
            discord.SelectOption(label=AMPHIBIAN, value=AMPHIBIAN),
            discord.SelectOption(label=INSECT, value=INSECT),
            discord.SelectOption(label=MOLLUSK, value=MOLLUSK),
            discord.SelectOption(label=CRUSTACEAN, value=CRUSTACEAN),
            discord.SelectOption(label=ARACHNID, value=ARACHNID),
            discord.SelectOption(label=CLITELLATA, value=CLITELLATA),
            discord.SelectOption(label=MYRIAPOD, value=MYRIAPOD),
            discord.SelectOption(label=ARTHROPOD, value=ARTHROPOD),
        ]

        dropdown = discord.ui.Select(placeholder=self.creature_class if self.creature_class else "Filter by class...", options=options, row=row)
        dropdown.callback = self.class_dropdown_callback()
        return dropdown
    def class_dropdown_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            selected_value = interaction.data['values'][0]
            self.creature_class = selected_value

            reloaded_image = self.reload_image(is_verbose=self.is_verbose, show_variants=self.show_variants, show_mythics=self.show_mythics, time=self.time, is_xl_mode=self.is_xl_mode, rarity=self.rarity, creature_class=self.creature_class)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def update_view_items(self):
        super().update_view_items()

        self.class_dropdown.placeholder = self.creature_class if self.creature_class else "Filter by class..."
        self.rarity_dropdown.placeholder = self.rarity if self.rarity else "Filter by rarity..."
        
        # Update toggle buttons appearance
        self.base_filter_expansion_button.style = discord.ButtonStyle.blurple if self.expanded_view_type == ENCYCLOPEDIA_BASE_EXPANDED_DISPLAY_KEY else discord.ButtonStyle.gray
        self.verbose_button.style = discord.ButtonStyle.green if self.is_verbose else discord.ButtonStyle.gray
        self.variants_button.style = discord.ButtonStyle.green if self.show_variants else discord.ButtonStyle.gray
        self.mythics_button.style = discord.ButtonStyle.blurple if self.show_mythics else discord.ButtonStyle.gray
        self.mythics_button.style = discord.ButtonStyle.blurple if self.show_mythics else discord.ButtonStyle.gray

        self.time_of_day_filter_expansion_button.style = discord.ButtonStyle.blurple if self.expanded_view_type == ENCYCLOPEDIA_EXPANDED_TIME_DISPLAY_KEY else discord.ButtonStyle.gray
        self.night_only_button.style = discord.ButtonStyle.blurple if self.time == NIGHT else discord.ButtonStyle.gray
        self.day_only_button.style = discord.ButtonStyle.blurple if self.time == DAY else discord.ButtonStyle.gray

        self.rarity_filter_expansion_button.style = discord.ButtonStyle.blurple if self.expanded_view_type == ENCYCLOPEDIA_EXPANDED_RARITY_DISPLAY_KEY else discord.ButtonStyle.gray
        self.class_filter_expansion_button.style = discord.ButtonStyle.blurple if self.expanded_view_type == ENCYCLOPEDIA_EXPANDED_CLASS_DISPLAY_KEY else discord.ButtonStyle.gray

        self.is_xl_button.style = discord.ButtonStyle.green if self.is_xl_mode else discord.ButtonStyle.gray
    def rebuild_view(self):
        super().rebuild_view()

        if self.is_xl_mode:
            self.remove_item(self.page_jump_dropdown)
            self.remove_item(self.prev_button)
            self.remove_item(self.next_button)

        # Add buttons to view
        self.add_item(self.base_filter_expansion_button)
        if self.expanded_view_type == ENCYCLOPEDIA_BASE_EXPANDED_DISPLAY_KEY:
            self.add_item(self.verbose_button)
            self.add_item(self.variants_button)
            self.add_item(self.mythics_button)

        if self.image_factory.environment.environment_id != 0:
            self.add_item(self.time_of_day_filter_expansion_button)
            self.add_item(self.rarity_filter_expansion_button)
            if self.expanded_view_type == ENCYCLOPEDIA_EXPANDED_TIME_DISPLAY_KEY:
                self.add_item(self.day_only_button)
                self.add_item(self.night_only_button)
            elif self.expanded_view_type == ENCYCLOPEDIA_EXPANDED_RARITY_DISPLAY_KEY:
                self.add_item(self.rarity_dropdown)

        self.add_item(self.class_filter_expansion_button)
        if self.expanded_view_type == ENCYCLOPEDIA_EXPANDED_CLASS_DISPLAY_KEY:
            self.add_item(self.class_dropdown)


        self.add_item(self.server_view_button)
        self.add_item(self.is_xl_button)


    def reload_image(self, target_user=None, is_verbose=None, show_variants=None, show_mythics=None, time=None, is_xl_mode=None, rarity=None, creature_class=None, new_page_number=None):
        new_image = self.image_factory.reload_image(target_user=target_user, is_verbose=is_verbose, show_variants=show_variants, show_mythics=show_mythics, time_of_day=time, is_xl_mode=is_xl_mode, rarity=rarity, creature_class=creature_class, new_page_number=new_page_number, )
        return convert_to_png(new_image, f'encyclopedia_page.png')


    # SUPPORT FUNCTIONS
    def update_time_filter(self, button_type):
        if button_type == ENCYCLOPEDIA_NIGHT_SPAWNS_DISPLAY_KEY:
            self.time = NIGHT if self.time != NIGHT else BOTH
        elif button_type == ENCYCLOPEDIA_DAY_SPAWNS_DISPLAY_KEY:
            self.time = DAY if self.time != DAY else BOTH
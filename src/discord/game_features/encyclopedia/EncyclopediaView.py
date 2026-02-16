import discord

from src.commons.CommonFunctions import convert_to_png, interaction_guard
from src.discord.game_features.encyclopedia.EncyclopediaImageFactory import EncyclopediaImageFactory
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.TGO_MMO_constants import NIGHT, BOTH, DAY, ENCYCLOPEDIA_VERBOSE_MODE, \
    ENCYCLOPEDIA_VARIANTS_MODE, ENCYCLOPEDIA_MYTHICAL_MODE, ENCYCLOPEDIA_NIGHT_SPAWNS_MODE, ENCYCLOPEDIA_DAY_SPAWNS_MODE

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

        # Initialize the buttons once
        self.verbose_button = self.create_toggle_button(ENCYCLOPEDIA_VERBOSE_MODE, row=2)
        self.variants_button = self.create_toggle_button(ENCYCLOPEDIA_VARIANTS_MODE, row=2)
        self.mythics_button = self.create_toggle_button(ENCYCLOPEDIA_MYTHICAL_MODE, row=2)
        self.day_only_button = self.create_toggle_button(ENCYCLOPEDIA_DAY_SPAWNS_MODE, row=2)
        self.night_only_button = self.create_toggle_button(ENCYCLOPEDIA_NIGHT_SPAWNS_MODE, row=2)

        # Add buttons to view
        self.refresh_view()


    # CREATE BUTTONS
    def create_toggle_button(self, button_type, row=1):
        data_options = {
            ENCYCLOPEDIA_VERBOSE_MODE: ["Show Detailed View", discord.ButtonStyle.green, None],
            ENCYCLOPEDIA_VARIANTS_MODE: ["Show Variants", discord.ButtonStyle.green, None],
            ENCYCLOPEDIA_MYTHICAL_MODE: ["Show Mythics", discord.ButtonStyle.green, "✨"],
            ENCYCLOPEDIA_NIGHT_SPAWNS_MODE: ["Show Night Spawns", discord.ButtonStyle.green, "🌙"],
            ENCYCLOPEDIA_DAY_SPAWNS_MODE: ["Show Day Spawns", discord.ButtonStyle.green, "☀️"]
        }
        data = data_options[button_type]
        button = discord.ui.Button(label=data[0], style=data[1], emoji=data[2], row=row)

        button.callback = self.toggle_callback(button_type)
        return button
    def toggle_callback(self, button_type):
        @interaction_guard()
        async def callback(interaction):
            await interaction.response.defer()

            self.is_verbose = not self.is_verbose if button_type == ENCYCLOPEDIA_VERBOSE_MODE else self.is_verbose
            self.show_variants = not self.show_variants if button_type == ENCYCLOPEDIA_VARIANTS_MODE else self.show_variants
            self.show_mythics = not self.show_mythics if button_type == ENCYCLOPEDIA_MYTHICAL_MODE else self.show_mythics
            self.update_time_filter(button_type)

            reloaded_image = self.reload_image(is_verbose=self.is_verbose, show_variants=self.show_variants, show_mythics=self.show_mythics, time=self.time)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback

    # FUNCTIONS FOR UPDATING VIEW STATE
    def update_view_items(self):
        super().update_view_items()
        
        # Update toggle buttons appearance
        self.verbose_button.style = discord.ButtonStyle.green if self.is_verbose else discord.ButtonStyle.gray
        self.variants_button.style = discord.ButtonStyle.green if self.show_variants else discord.ButtonStyle.gray
        self.mythics_button.style = discord.ButtonStyle.blurple if self.show_mythics else discord.ButtonStyle.gray
        self.mythics_button.style = discord.ButtonStyle.blurple if self.show_mythics else discord.ButtonStyle.gray
        self.night_only_button.style = discord.ButtonStyle.blurple if self.time == NIGHT else discord.ButtonStyle.gray
        self.day_only_button.style = discord.ButtonStyle.blurple if self.time == DAY else discord.ButtonStyle.gray
    def rebuild_view(self):
        super().rebuild_view()

        # Add buttons to view
        self.add_item(self.verbose_button)
        self.add_item(self.variants_button)
        self.add_item(self.mythics_button)

        if self.image_factory.environment.environment_id != 0:
            self.add_item(self.day_only_button)
            self.add_item(self.night_only_button)


    def reload_image(self, is_verbose=None, show_variants=None, show_mythics=None, time=None, new_page_number=None):
        new_image = self.image_factory.reload_image(is_verbose=is_verbose, show_variants=show_variants, show_mythics=show_mythics, time_of_day=time, new_page_number=new_page_number)
        return convert_to_png(new_image, f'encyclopedia_page.png')


    # SUPPORT FUNCTIONS
    def update_time_filter(self, button_type):
        if button_type == ENCYCLOPEDIA_NIGHT_SPAWNS_MODE:
            self.time = NIGHT if self.time != NIGHT else BOTH
        elif button_type == ENCYCLOPEDIA_DAY_SPAWNS_MODE:
            self.time = DAY if self.time != DAY else BOTH
import asyncio
import discord
from discord.ui import Select

from src.commons.CommonFunctions import convert_to_png
from src.commons.CommonFunctions import retry_on_ssl_error
from src.commons.CommonViewComponents import create_go_back_button, create_close_button, create_navigation_button, create_page_jump_dropdown
from src.discord.game_features.encyclopedia.EncyclopediaImageFactory import EncyclopediaImageFactory
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.TGO_MMO_constants import NIGHT, BOTH, DAY

#todo: move to commons
verbose_keyword = "verbose"
variants_keyword = "variants"
mythics_keyword = "mythics"
night_spawns_keyword = "night_spawns"
day_spawns_keyword = "day_spawns"

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
        self.page_jump_dropdown = create_page_jump_dropdown(view_instance=self, row=0)

        self.verbose_button = self.create_toggle_button(verbose_keyword, row=2)
        self.variants_button = self.create_toggle_button(variants_keyword, row=2)
        self.mythics_button = self.create_toggle_button(mythics_keyword, row=2)
        self.day_only_button = self.create_toggle_button(day_spawns_keyword, row=2)
        self.night_only_button = self.create_toggle_button(night_spawns_keyword, row=2)

        # Add buttons to view
        self.refresh_view()


    # CREATE BUTTONS
    def create_toggle_button(self, button_type, row=1):
        data_options = {
            verbose_keyword: ["Show Detailed View", discord.ButtonStyle.green, None],
            variants_keyword: ["Show Variants", discord.ButtonStyle.green, None],
            mythics_keyword: ["Show Mythics", discord.ButtonStyle.green, "✨"],
            night_spawns_keyword: ["Show Night Spawns", discord.ButtonStyle.green, "🌙"],
            day_spawns_keyword: ["Show Day Spawns", discord.ButtonStyle.green, "☀️"]
        }
        data = data_options[button_type]
        button = discord.ui.Button(label=data[0], style=data[1], emoji=data[2], row=row)

        button.callback = self.toggle_callback(button_type)
        return button
    def toggle_callback(self, button_type):
        @retry_on_ssl_error()
        async def callback(interaction):
            await interaction.response.defer()

            self.is_verbose = not self.is_verbose if button_type == verbose_keyword else self.is_verbose
            self.show_variants = not self.show_variants if button_type == variants_keyword else self.show_variants
            self.show_mythics = not self.show_mythics if button_type == mythics_keyword else self.show_mythics
            self.update_time_filter(button_type)

            reloaded_image = self.reload_image(is_verbose=self.is_verbose, show_variants=self.show_variants, show_mythics=self.show_mythics, time=self.time)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback


    # CREATE DROPDOWNS
    def create_page_jump_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Page {i}", value=str(i)) for i in range(1, self.image_factory.total_pages)]
        dropdown = Select(placeholder="Skip to Page", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.page_jump_callback
        return dropdown
    async def page_jump_callback(self):
        @retry_on_ssl_error()
        async def callback(interaction):
            await interaction.response.defer()

            self.image_factory.page_num = int(interaction.data["values"][0])

            self.refresh_view()
            await interaction.message.edit(attachments=[self.image_factory.reload_image()], view=self)

    # FUNCTIONS FOR UPDATING VIEW STATE
    def update_view_items(self):
        super().update_view_items()
        # Update navigation buttons
        # Update Options
        self.page_jump_dropdown.options = [discord.SelectOption(label=f"Page {i}", value=str(i)) for i in range(1, self.image_factory.total_pages + 1)]
        self.page_jump_dropdown.placeholder = f"Page {self.image_factory.page_num}"  # Set current page as placeholder

        # Update Enabled/Disabled States
        self.page_jump_dropdown.disabled = self.image_factory.total_pages == 1

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
        self.add_item(self.page_jump_dropdown)

        self.add_item(self.verbose_button)
        self.add_item(self.variants_button)
        self.add_item(self.mythics_button)

        if self.image_factory.environment.environment_id != 0:
            self.add_item(self.day_only_button)
            self.add_item(self.night_only_button)


    def reload_image(self, is_verbose=None, show_variants=None, show_mythics=None, time=None, new_page_number=None):
        print('bizz')

        new_image = self.image_factory.reload_image(is_verbose=is_verbose, show_variants=show_variants, show_mythics=show_mythics, time_of_day=time, new_page_number=new_page_number)
        return convert_to_png(new_image, f'encyclopedia_page.png')

    def update_time_filter(self, button_type):
        if button_type == night_spawns_keyword:
            self.time = NIGHT if self.time != NIGHT else BOTH
        elif button_type == day_spawns_keyword:
            self.time = DAY if self.time != DAY else BOTH
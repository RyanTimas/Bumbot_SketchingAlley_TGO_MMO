import asyncio
import discord
from discord.ui import Select

from src.commons.CommonFunctions import convert_to_png, interaction_guard
from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view
from src.commons.CommonViewComponents import create_go_back_button, create_close_button, create_navigation_button, \
    create_page_jump_dropdown
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.encyclopedia.EncyclopediaImageFactory import EncyclopediaImageFactory
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.TGO_MMO_constants import NIGHT, BOTH, DAY

verbose_keyword = "verbose"
variants_keyword = "variants"
mythics_keyword = "mythics"
night_spawns_keyword = "night_spawns"
day_spawns_keyword = "day_spawns"

next_ = "next"
previous = "previous"
jump = "jump"

class EncyclopediaView(BaseView):
    def __init__(self, message_author, target_user, encyclopedia_image_factory: EncyclopediaImageFactory, is_verbose=False, show_variants=False, show_mythics=False, time=BOTH, original_view=None, original_image_files=[]):
        super().__init__(message_author=message_author, target_user=target_user, image_factory=encyclopedia_image_factory, original_view=original_view)
        self.original_image_files = original_image_files

        self.is_verbose = is_verbose
        self.show_variants = show_variants
        self.show_mythics = show_mythics
        self.time = time
        self.new_page = 1

        # Initialize the buttons once
        self.page_jump_dropdown = create_page_jump_dropdown(view_instance=self, row=0)

        self.prev_button = create_navigation_button(is_next=False, view_instance=self, row=1)
        self.next_button = create_navigation_button(is_next=True, view_instance=self, row=1)

        self.verbose_button = self.create_toggle_button(verbose_keyword, row=2)
        self.variants_button = self.create_toggle_button(variants_keyword, row=2)
        self.mythics_button = self.create_toggle_button(mythics_keyword, row=2)
        self.day_only_button = self.create_toggle_button(day_spawns_keyword, row=2)
        self.night_only_button = self.create_toggle_button(night_spawns_keyword, row=2)

        self.close_button = create_close_button(interaction_lock=self.interaction_lock, message_author_id=self.message_author.user_id, row=3)
        self.go_back_button = create_go_back_button(original_view=self.original_view, row=3, interaction_lock=self.interaction_lock, message_author_id=self.message_author.user_id, files=self.original_image_files)

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
            self.is_verbose = not self.is_verbose if button_type == verbose_keyword else self.is_verbose
            self.show_variants = not self.show_variants if button_type == variants_keyword else self.show_variants
            self.show_mythics = not self.show_mythics if button_type == mythics_keyword else self.show_mythics
            self.time = NIGHT if button_type == night_spawns_keyword and self.time != NIGHT else (DAY if button_type == day_spawns_keyword and self.time != DAY else BOTH)

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
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
            self.new_page = int(interaction.data["values"][0])

            self.update_button_states()
            await interaction.message.edit(attachments=[self.image_factory.build_encyclopedia_page_image()], view=self)

    # FUNCTIONS FOR UPDATING VIEW STATE
    def update_button_states(self):
        # Update navigation buttons
        current_page = self.image_factory.page_num
        total_pages = self.image_factory.total_pages

        # Update Options
        self.page_jump_dropdown.options = [discord.SelectOption(label=f"Page {i}", value=str(i)) for i in range(1, total_pages + 1)]
        self.page_jump_dropdown.placeholder = f"Page {current_page}"  # Set current page as placeholder

        # Update Enabled/Disabled States
        self.page_jump_dropdown.disabled = total_pages == 1
        self.prev_button.disabled = current_page == 1
        self.next_button.disabled = current_page == total_pages

        # Update toggle buttons appearance
        self.verbose_button.style = discord.ButtonStyle.green if self.is_verbose else discord.ButtonStyle.gray
        self.variants_button.style = discord.ButtonStyle.green if self.show_variants else discord.ButtonStyle.gray
        self.mythics_button.style = discord.ButtonStyle.blurple if self.show_mythics else discord.ButtonStyle.gray
        self.mythics_button.style = discord.ButtonStyle.blurple if self.show_mythics else discord.ButtonStyle.gray
        self.night_only_button.style = discord.ButtonStyle.blurple if self.time == NIGHT else discord.ButtonStyle.gray
        self.day_only_button.style = discord.ButtonStyle.blurple if self.time == DAY else discord.ButtonStyle.gray
    def rebuild_view(self):
        for item in self.children.copy():
            self.remove_item(item)

        # Add buttons to view
        self.add_item(self.page_jump_dropdown)
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

        self.add_item(self.verbose_button)
        self.add_item(self.variants_button)
        self.add_item(self.mythics_button)

        if self.image_factory.environment.environment_id != 0:
            self.add_item(self.day_only_button)
            self.add_item(self.night_only_button)

        self.add_item(self.close_button)
        if self.original_view is not None:
            self.add_item(self.go_back_button)

    def reload_image(self, new_page_number=None):
        new_image = self.image_factory.build_encyclopedia_page_image(new_page_number=self.new_page, is_verbose=self.is_verbose, show_variants=self.show_variants, show_mythics=self.show_mythics, time_of_day=self.time)
        return convert_to_png(new_image, f'encyclopedia_page.png')
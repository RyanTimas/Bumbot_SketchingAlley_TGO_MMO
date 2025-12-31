import asyncio
import discord
from discord.ui import Select

from src.commons.CommonFunctions import convert_to_png, create_go_back_button, create_close_button
from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.encyclopedia.EncyclopediaImageFactory import EncyclopediaImageFactory

verbose_keyword = "verbose"
variants_keyword = "variants"
mythics_keyword = "mythics"
night_spawns_keyword = "night_spawns"
day_spawns_keyword = "day_spawns"

day = "day"
night = "night"
both = "both"

next_ = "next"
previous = "previous"
jump = "jump"

class EncyclopediaView(discord.ui.View):
    def __init__(self, message_author, encyclopedia_image_factory: EncyclopediaImageFactory, is_verbose=False, show_variants=False, show_mythics=False, time=both, original_view=None):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.encyclopedia_image_factory = encyclopedia_image_factory

        self.original_view = original_view
        self.interaction_lock = asyncio.Lock()

        self.is_verbose = is_verbose
        self.show_variants = show_variants
        self.show_mythics = show_mythics
        self.time = time
        self.new_page = 1

        # Initialize the buttons once
        self.page_jump_dropdown = self.create_page_jump_dropdown(row=0)

        self.prev_button = self.create_navigation_button(is_next=False, row=1)
        self.page_jump_button = self.create_advanced_navigation_button(row=1)
        self.next_button = self.create_navigation_button(is_next=True, row=1)

        self.verbose_button = self.create_toggle_button(verbose_keyword, row=2)
        self.variants_button = self.create_toggle_button(variants_keyword, row=2)
        self.mythics_button = self.create_toggle_button(mythics_keyword, row=2)
        self.day_only_button = self.create_toggle_button(day_spawns_keyword, row=2)
        self.night_only_button = self.create_toggle_button(night_spawns_keyword, row=2)

        self.close_button = create_close_button(interaction_lock=self.interaction_lock, message_author_id=self.message_author.id, row=3)
        self.go_back_button = create_go_back_button(original_view=self.original_view, row=3, interaction_lock=self.interaction_lock, message_author_id=self.message_author.id)

        # Add buttons to view
        self.add_item(self.page_jump_dropdown)
        self.add_item(self.prev_button)
        self.add_item(self.page_jump_button)
        self.add_item(self.next_button)

        self.add_item(self.verbose_button)
        self.add_item(self.variants_button)
        if get_tgommo_db_handler().get_server_mythical_count() > 0:
            self.add_item(self.mythics_button)
        self.add_item(self.day_only_button)
        self.add_item(self.night_only_button)

        self.add_item(self.close_button)
        if self.original_view is not None:
            self.add_item(self.go_back_button)

        self.refresh_view()


    # CREATE BUTTONS
    def create_navigation_button(self, is_next, row=0):
        button = discord.ui.Button(
            label="To Next Page➡️" if is_next else "⬅️To Previous Page",
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.nav_callback(new_page=next_ if is_next else previous)
        return button
    def create_advanced_navigation_button(self, row):
        button = discord.ui.Button(
            label="⬆️ Jump To Page ⬆️️",
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.nav_callback(new_page=jump)
        return button
    def nav_callback(self, new_page,):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                # Update page number
                page_options = {
                    next_: self.encyclopedia_image_factory.page_num + 1,
                    previous: self.encyclopedia_image_factory.page_num -1,
                   jump: self.new_page
                }

                new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(new_page_number=page_options[new_page])

                # Update state and button appearance
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'encyclopedia_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def create_toggle_button(self, button_type, row=1):
        labels = {
            verbose_keyword: "Show Detailed View",
            variants_keyword: "Show Variants",
            mythics_keyword: "Show Mythics",
            night_spawns_keyword: "Show Night Spawns",
            day_spawns_keyword: "Show Day Spawns",
        }
        styles = {
            verbose_keyword: discord.ButtonStyle.green,
            variants_keyword: discord.ButtonStyle.green,
            mythics_keyword: discord.ButtonStyle.green,
            night_spawns_keyword: discord.ButtonStyle.green,
            day_spawns_keyword: discord.ButtonStyle.green
        }
        emojis = {
            verbose_keyword: None,
            variants_keyword: None,
            mythics_keyword: "✨",
            night_spawns_keyword: "🌙",
            day_spawns_keyword: "☀️"
        }

        button = discord.ui.Button(
            label=labels[button_type],
            style=styles[button_type],
            emoji=emojis[button_type],
            row=row
        )
        button.callback = self.toggle_callback(button_type)
        return button
    def toggle_callback(self, button_type):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                # Toggle the appropriate state
                if button_type == verbose_keyword:
                    self.is_verbose = not self.is_verbose
                    new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(is_verbose=self.is_verbose)
                elif button_type == variants_keyword:
                    self.show_variants = not self.show_variants
                    new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(show_variants=self.show_variants)
                elif button_type == mythics_keyword:
                    self.show_mythics = not self.show_mythics
                    new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(show_mythics=self.show_mythics)
                elif button_type == night_spawns_keyword:
                    self.time = night if self.time != night else both
                    new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(show_only_day_spawns=self.time == day, show_only_night_spawns=self.time == night)
                elif button_type == day_spawns_keyword:
                    self.time = day if self.time != day else both
                    new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(show_only_day_spawns=self.time == day, show_only_night_spawns=self.time == night)

                file = convert_to_png(new_image, f'encyclopedia_page.png')
                self.update_button_states()

                await interaction.message.edit(attachments=[file], view=self)

        return callback


    # CREATE DROPDOWNS
    def create_page_jump_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Page {i}", value=str(i)) for i in range(1, self.encyclopedia_image_factory.total_pages)]
        dropdown = Select(placeholder="Skip to Page", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.page_jump_callback
        return dropdown
    async def page_jump_callback(self, interaction: discord.Interaction):
        self.new_page = int(interaction.data["values"][0])
        await interaction.response.defer()

    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        # Update navigation buttons
        current_page = self.encyclopedia_image_factory.page_num
        total_pages = self.encyclopedia_image_factory.total_pages

        # Update Options
        self.page_jump_dropdown.options = [discord.SelectOption(label=f"Page {i}", value=str(i)) for i in range(1, total_pages + 1)]

        # Update Enabled/Disabled States
        self.page_jump_dropdown.disabled = total_pages == 1
        self.prev_button.disabled = current_page == 1
        self.page_jump_button.disabled = total_pages == 1
        self.next_button.disabled = current_page == total_pages

        # Update toggle buttons appearance
        self.verbose_button.style = discord.ButtonStyle.green if self.is_verbose else discord.ButtonStyle.gray
        self.variants_button.style = discord.ButtonStyle.green if self.show_variants else discord.ButtonStyle.gray
        self.mythics_button.style = discord.ButtonStyle.blurple if self.show_mythics else discord.ButtonStyle.gray
        self.mythics_button.style = discord.ButtonStyle.blurple if self.show_mythics else discord.ButtonStyle.gray
        self.night_only_button.style = discord.ButtonStyle.blurple if self.time == night else discord.ButtonStyle.gray
        self.day_only_button.style = discord.ButtonStyle.blurple if self.time == day else discord.ButtonStyle.gray
    def rebuild_view(self):
        for item in self.children.copy():
            self.remove_item(item)

        # Add buttons to view
        self.add_item(self.page_jump_dropdown)
        self.add_item(self.prev_button)
        self.add_item(self.page_jump_button)
        self.add_item(self.next_button)

        self.add_item(self.verbose_button)
        self.add_item(self.variants_button)
        if get_tgommo_db_handler().get_server_mythical_count() > 0:
            self.add_item(self.mythics_button)
        self.add_item(self.day_only_button)
        self.add_item(self.night_only_button)

        self.add_item(self.close_button)
        if self.original_view is not None:
            self.add_item(self.go_back_button)
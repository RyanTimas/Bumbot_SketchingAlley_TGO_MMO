import asyncio
import discord
from src.commons.CommonFunctions import convert_to_png, create_go_back_button
from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.image_factories.EncyclopediaImageFactory import EncyclopediaImageFactory

verbose_keyword = "verbose"
variants_keyword = "variants"
mythics_keyword = "mythics"
night_spawns_keyword = "night_spawns"
day_spawns_keyword = "day_spawns"

class EncyclopediaView(discord.ui.View):
    def __init__(self, message_author, encyclopedia_image_factory: EncyclopediaImageFactory, is_verbose=False, show_variants=False, show_mythics=False, original_view=None):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.encyclopedia_image_factory = encyclopedia_image_factory
        self.is_verbose = is_verbose
        self.show_variants = show_variants
        self.show_mythics = show_mythics
        self.original_view = original_view
        # Add a lock to prevent concurrent button interactions
        self.interaction_lock = asyncio.Lock()

        # Initialize the buttons once
        self.verbose_button = self.create_toggle_button(verbose_keyword)
        self.variants_button = self.create_toggle_button(variants_keyword)
        self.mythics_button = self.create_toggle_button(mythics_keyword)

        self.prev_button = self.create_navigation_button(is_next=False)
        self.next_button = self.create_navigation_button(is_next=True)

        self.close_button = self.create_close_button()
        self.go_back_button = create_go_back_button(original_view=self.original_view, row=2, interaction_lock=self.interaction_lock, message_author_id=self.message_author.id)

        # Add buttons to view
        self.add_item(self.prev_button)
        self.add_item(self.verbose_button)
        self.add_item(self.variants_button)

        if get_tgommo_db_handler().get_server_mythical_count() > 0:
            self.add_item(self.mythics_button)

        self.add_item(self.next_button)

        self.add_item(self.close_button)
        self.add_item(self.go_back_button)

        # Update button states
        self.update_button_states()


    # create buttons
    def create_navigation_button(self, is_next):
        button = discord.ui.Button(
            label="To Next Page➡️" if is_next else "⬅️To Previous Page",
            style=discord.ButtonStyle.blurple,
            row=0
        )
        button.callback = self.nav_callback(is_next)
        return button
    def nav_callback(self, is_next):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                # Update page number
                new_page = self.encyclopedia_image_factory.page_num + (1 if is_next else -1)
                new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(new_page_number=new_page)

                # Update state and button appearance
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'encyclopedia_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback


    def create_toggle_button(self, button_type):
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
            row=1
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

                # Update button states
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'encyclopedia_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def create_close_button(self):
        button = discord.ui.Button(
            label="✘",
            style=discord.ButtonStyle.red,
            row=2  # Place in third row
        )
        button.callback = self.close_callback()
        return button
    def close_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            # For delete operation, we need a shorter lock
            async with self.interaction_lock:
                # Delete the message
                await interaction.message.delete()

        return callback


    # handle button behavior
    def update_button_states(self):
        # Update navigation buttons
        current_page = self.encyclopedia_image_factory.page_num
        total_pages = self.encyclopedia_image_factory.total_pages

        self.prev_button.disabled = current_page == 1
        self.next_button.disabled = current_page == total_pages

        # Update toggle buttons appearance
        self.verbose_button.style = discord.ButtonStyle.green if self.is_verbose else discord.ButtonStyle.gray
        self.variants_button.style = discord.ButtonStyle.green if self.show_variants else discord.ButtonStyle.gray
        self.mythics_button.style = discord.ButtonStyle.blurple if self.show_mythics else discord.ButtonStyle.gray
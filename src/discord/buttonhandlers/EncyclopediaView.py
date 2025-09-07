import asyncio
import functools

import aiohttp
import discord
from anyio import current_time
from discord import Message
from discord.ui import View

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.image_factories.EncyclopediaImageFactory import EncyclopediaImageFactory


import asyncio
import functools

import aiohttp
import discord

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.image_factories.EncyclopediaImageFactory import EncyclopediaImageFactory


class EncyclopediaView(discord.ui.View):
    def __init__(self, message_author: int, encyclopedia_image_factory: EncyclopediaImageFactory, is_verbose=False, show_variants=False, show_mythics=False):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.encyclopedia_image_factory = encyclopedia_image_factory
        self.is_verbose = is_verbose
        self.show_variants = show_variants
        self.show_mythics = show_mythics
        # Add a lock to prevent concurrent button interactions
        self.interaction_lock = asyncio.Lock()

        # Initialize the buttons once
        self.verbose_button = self.create_toggle_button("verbose")
        self.variants_button = self.create_toggle_button("variants")
        self.mythics_button = self.create_toggle_button("mythics")

        self.prev_button = self.create_navigation_button(is_next=False)
        self.next_button = self.create_navigation_button(is_next=True)

        self.close_button = self.create_close_button()

        # Add buttons to view
        self.add_item(self.prev_button)
        self.add_item(self.verbose_button)
        self.add_item(self.variants_button)

        if get_tgommo_db_handler().get_server_mythical_count() > 0:
            self.add_item(self.mythics_button)

        self.add_item(self.next_button)

        self.add_item(self.close_button)

        # Update button states
        self.update_button_states()

    def create_close_button(self):
        button = discord.ui.Button(
            label="close",
            style=discord.ButtonStyle.red,
            row=2  # Place in third row
        )
        button.callback = self.close_callback()
        return button

    def create_navigation_button(self, is_next):
        button = discord.ui.Button(
            label="To Next Page➡️" if is_next else "⬅️To Previous Page",
            style=discord.ButtonStyle.blurple,
            row=0
        )
        button.callback = self.nav_callback(is_next)
        return button

    def create_toggle_button(self, button_type):
        labels = {
            "verbose": "Show Detailed View",
            "variants": "Show Variants",
            "mythics": "Show Mythics"
        }
        styles = {
            "verbose": discord.ButtonStyle.green,
            "variants": discord.ButtonStyle.green,
            "mythics": discord.ButtonStyle.green
        }
        emojis = {
            "verbose": None,
            "variants": None,
            "mythics": "✨"
        }

        button = discord.ui.Button(
            label=labels[button_type],
            style=styles[button_type],
            emoji=emojis[button_type],
            row=1
        )
        button.callback = self.toggle_callback(button_type)
        return button

    def nav_callback(self, is_next):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if self.interaction_lock.locked():
                await interaction.response.send_message("Please wait for the current action to complete.", ephemeral=True)
                return

            if interaction.user.id != self.message_author:
                await interaction.response.send_message("Only the user who used this command may interact with this screen.", ephemeral=True)
                return

            # Acquire lock to prevent concurrent actions
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

    def toggle_callback(self, button_type):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if self.interaction_lock.locked():
                return

            if interaction.user.id != self.message_author:
                await interaction.response.send_message(
                    "Only the user who used this command may interact with this screen.",
                    ephemeral=True
                )
                return

            # Acquire lock to prevent concurrent actions
            async with self.interaction_lock:
                await interaction.response.defer()

                # Toggle the appropriate state
                if button_type == "verbose":
                    self.is_verbose = not self.is_verbose
                    new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(is_verbose=self.is_verbose)
                elif button_type == "variants":
                    self.show_variants = not self.show_variants
                    new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(show_variants=self.show_variants)
                elif button_type == "mythics":
                    self.show_mythics = not self.show_mythics
                    new_image = self.encyclopedia_image_factory.build_encyclopedia_page_image(show_mythics=self.show_mythics)

                # Update button states
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'encyclopedia_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def close_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if self.interaction_lock.locked():
                await interaction.response.send_message("Please wait for the current action to complete.", ephemeral=True)
                return

            if interaction.user.id != self.message_author:
                await interaction.response.send_message(
                    "Only the user who used this command may interact with this screen.",
                    ephemeral=True
                )
                return

            # For delete operation, we need a shorter lock
            async with self.interaction_lock:
                # Delete the message
                await interaction.message.delete()

        return callback

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

# Retry decorator for handling SSL errors
def retry_on_ssl_error(max_retries=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except discord.errors.InteractionResponded:
                    # Interaction already responded to, so don't retry
                    return
                except aiohttp.client_exceptions.ClientOSError as e:
                    if "SSL" in str(e) and retries < max_retries - 1:
                        retries += 1
                        await asyncio.sleep(delay)
                    else:
                        # If we've exhausted retries or it's not an SSL error, re-raise
                        raise
        return wrapper
    return decorator
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


class EncyclopediaPageButton(discord.ui.Button):
    def __init__(self, message_author: int, encyclopedia_image_factory: EncyclopediaImageFactory, current_page:int, total_pages:int, is_next:bool, is_verbose = False, show_variants = False, show_mythics= False, is_disabled:bool=False, button_type:str='shift', row:int=1):
        label = ""
        style = discord.ButtonStyle.grey

        if button_type == 'shift':
            label = "To Next Page➡️" if is_next else "⬅️To Previous Page"
            emoji = '➡️' if is_next else '⬅️'
            style = discord.ButtonStyle.red if not is_disabled else discord.ButtonStyle.grey
        elif button_type == 'verbose':
            label = "Show Detailed View"
            style = discord.ButtonStyle.green if not is_verbose else discord.ButtonStyle.gray
        elif button_type == 'show_variant':
            label = "Show Variants"
            style = discord.ButtonStyle.green if not show_variants else discord.ButtonStyle.gray
        elif button_type == 'show_mythics':
            label = "✨ Show Mythics"
            style = discord.ButtonStyle.blurple if not show_mythics else discord.ButtonStyle.gray

        super().__init__(label=label, style=style, disabled=is_disabled, row=row)
        self.message_author = message_author
        self.encyclopedia_image_factory = encyclopedia_image_factory
        self.button_type = button_type

        self.current_page = (current_page + 1 if is_next else current_page - 1) if button_type == 'shift' else current_page
        self.total_pages = total_pages
        self.is_next = is_next
        self.is_verbose = is_verbose
        self.show_variants = show_variants
        self.show_mythics = show_mythics

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.message_author:
            await interaction.response.send_message("Only the user who used this command may interact with this screen. Type !caught_creatures to open your own.", ephemeral=True)
            return

        await interaction.response.defer()

        new_encyclopedia_page = None
        if self.button_type == 'shift':
            new_encyclopedia_page = self.encyclopedia_image_factory.build_encyclopedia_page_image(new_page_number=self.current_page)
        elif self.button_type == 'verbose':
            new_encyclopedia_page = self.encyclopedia_image_factory.build_encyclopedia_page_image(is_verbose= self.is_verbose)
        elif self.button_type == 'show_variant':
            new_encyclopedia_page = self.encyclopedia_image_factory.build_encyclopedia_page_image(show_variants= self.show_variants)
        elif self.button_type == 'show_mythics':
            new_encyclopedia_page = self.encyclopedia_image_factory.build_encyclopedia_page_image(show_mythics= self.show_mythics)

        self.total_pages = self.encyclopedia_image_factory.total_pages
        self.current_page = self.encyclopedia_image_factory.page_num

        # Add Buttons to View:   order -> previous page button, verbose button, show variants button, next page button
        new_view = View()

        new_view.add_item(EncyclopediaPageButton(button_type= 'shift',          current_page=self.current_page, total_pages=self.total_pages, is_next=False,  is_verbose=self.is_verbose,         show_variants= self.show_variants,        show_mythics= self.show_mythics,    is_disabled=self.current_page == 1, encyclopedia_image_factory=self.encyclopedia_image_factory, message_author=self.message_author, row=1))
        new_view.add_item(EncyclopediaPageButton(button_type= 'verbose',        current_page=self.current_page, total_pages=self.total_pages, is_next=False,  is_verbose= not self.is_verbose,    show_variants= self.show_variants,        show_mythics= self.show_mythics,    is_disabled=False, encyclopedia_image_factory=self.encyclopedia_image_factory, message_author=self.message_author))
        new_view.add_item(EncyclopediaPageButton(button_type= 'show_variant',   current_page=self.current_page, total_pages=self.total_pages, is_next=False,  is_verbose= self.is_verbose,        show_variants= not self.show_variants,    show_mythics= self.show_mythics,    is_disabled=False, encyclopedia_image_factory=self.encyclopedia_image_factory, message_author=self.message_author))

        new_view.add_item(EncyclopediaPageButton(button_type= 'show_mythics',   current_page=self.current_page, total_pages=self.total_pages, is_next=False,  is_verbose= self.is_verbose,        show_variants= self.show_variants,        show_mythics= not self.show_mythics,    is_disabled=False, encyclopedia_image_factory=self.encyclopedia_image_factory, message_author=self.message_author))
        new_view.add_item(EncyclopediaPageButton(button_type= 'shift',          current_page=self.current_page, total_pages=self.total_pages, is_next=True,   is_verbose=self.is_verbose,         show_variants= self.show_variants,        show_mythics= self.show_mythics,    is_disabled= self.current_page == self.total_pages, encyclopedia_image_factory=self.encyclopedia_image_factory, message_author=self.message_author, row=1))

        file = convert_to_png(new_encyclopedia_page, f'encyclopedia_page.png')

        await interaction.message.edit(attachments=[file], view=new_view)


class EncyclopediaPageShiftView(View):
    def __init__(self, encyclopedia_image_factory:EncyclopediaImageFactory, current_page:int, total_pages:int, is_verbose:bool, show_variants:bool=False, show_mythics:bool=False, message_author: int = 0):
        super().__init__(timeout=None)

        mythics_unlocked = get_tgommo_db_handler().get_server_mythical_count() > 0


        # Add Buttons to View:   order -> previous page button, verbose button, next page button
        self.add_item(EncyclopediaPageButton(button_type= 'shift',          current_page=current_page, total_pages=total_pages, is_next=False,  is_verbose=  is_verbose,    show_variants=  show_variants,      show_mythics= show_mythics,         is_disabled=current_page == 1,              encyclopedia_image_factory=encyclopedia_image_factory, message_author=message_author, row=1))
        self.add_item(EncyclopediaPageButton(button_type= 'verbose',        current_page=current_page, total_pages=total_pages, is_next=False,  is_verbose= not is_verbose, show_variants=  show_variants,      show_mythics= show_mythics,         is_disabled=False,                          encyclopedia_image_factory=encyclopedia_image_factory, message_author=message_author))
        self.add_item(EncyclopediaPageButton(button_type= 'show_variant',   current_page=current_page, total_pages=total_pages, is_next=False,  is_verbose=  is_verbose,    show_variants= not show_variants,   show_mythics= show_mythics,         is_disabled=False,                          encyclopedia_image_factory=encyclopedia_image_factory, message_author=message_author))

        if mythics_unlocked:
            self.add_item(EncyclopediaPageButton(button_type= 'show_mythics',   current_page=current_page, total_pages=total_pages, is_next=False,  is_verbose=  is_verbose,    show_variants=  show_variants,      show_mythics= not show_mythics,     is_disabled=False,                          encyclopedia_image_factory=encyclopedia_image_factory, message_author=message_author))

        self.add_item(EncyclopediaPageButton(button_type= 'shift',          current_page=current_page, total_pages=total_pages, is_next=True,   is_verbose=  is_verbose,    show_variants=  show_variants,      show_mythics= show_mythics,         is_disabled=current_page == total_pages,    encyclopedia_image_factory=encyclopedia_image_factory, message_author=message_author, row=1))
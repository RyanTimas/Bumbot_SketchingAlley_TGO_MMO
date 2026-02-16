import asyncio
import discord

from src.commons.CommonFunctions import convert_to_png, retry_on_ssl_error, interaction_guard
from src.commons.CommonViewComponents import create_go_back_button, create_close_button
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.discord.objects.TGOPlayer import TGOPlayer


class BaseView(discord.ui.View):
    def __init__(self, message_author: TGOPlayer, target_user: TGOPlayer,  image_factory=None, original_view=None, original_view_files=[]):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.target_user = target_user
        self.image_factory = image_factory if image_factory else BaseImageFactory(message_author=message_author, target_user=target_user)
        self.original_view = original_view
        self.original_image_files = original_view_files

        self.page_num = 1

        self.interaction_lock = asyncio.Lock()

        # BUTTONS
        self.page_jump_dropdown = self.create_page_jump_dropdown(row=0)
        self.prev_button = self.create_navigation_button(is_next=False, row=1)
        self.next_button = self.create_navigation_button(is_next=True, row=1)

        self.go_back_button = create_go_back_button(original_view=self.original_view, interaction_lock=self.interaction_lock, message_author_id=self.message_author.user_id, files=self.original_image_files, row=4)
        self.close_button = create_close_button(interaction_lock=self.interaction_lock, message_author_id=self.message_author.user_id, row=4, )

    # BUTTONS
    def create_navigation_button(self, is_next, callback_func=None, row=0, disabled=False):
        button = discord.ui.Button(label="To Next Page➡️" if is_next else "⬅️To Previous Page", style=discord.ButtonStyle.blurple, row=row, disabled=disabled)
        button.callback = callback_func if callback_func else self.navigation_button_callback(is_next)
        return button
    def navigation_button_callback(self, is_next):
        @interaction_guard(max_retries=3, delay=1)
        async def callback(interaction):
            await interaction.response.defer()

            new_page_number = self.image_factory.page_num + (1 if is_next else -1)

            reloaded_image = self.reload_image(new_page_number=new_page_number)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback

    # DROPDOWNS
    def create_page_jump_dropdown(self, row=0):
        options = [discord.SelectOption(label=f"Page {i}", value=str(i)) for i in range(1, self.image_factory.total_pages + 1)]
        dropdown = discord.ui.Select(placeholder="Skip to Page", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.page_jump_callback()
        return dropdown
    def page_jump_callback(self):
        @interaction_guard(max_retries=3, delay=1)
        async def callback(interaction):
            await interaction.response.defer()

            new_page_number = int(interaction.data["values"][0])

            reloaded_image = self.reload_image(new_page_number=new_page_number)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_view_items()
        self.rebuild_view()
    def update_view_items(self):
        # update labels

        # update disabled state
        self.prev_button.disabled = self.image_factory.page_num == 1
        self.next_button.disabled = self.image_factory.page_num == self.image_factory.total_pages
        self.page_jump_dropdown.disabled = self.image_factory.total_pages == 1

        # update options
        self.page_jump_dropdown.options = [discord.SelectOption(label=f"Page {i}", value=str(i), default=(i == self.image_factory.page_num)) for i in range(1, self.image_factory.total_pages + 1)]

        # update placeholders
        self.page_jump_dropdown.placeholder = f"Page {self.image_factory.page_num}"

        # update styles
        pass

    def rebuild_view(self):
        self.clear_items()

        if self.image_factory and self.image_factory.total_pages > 1:
            self.add_item(self.page_jump_dropdown)
            self.add_item(self.prev_button)
            self.add_item(self.next_button)

        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)

    def reload_image(self, image_factory= None, new_page_number=None):
        print('buzz')
        image_factory =  image_factory if image_factory else self.image_factory
        new_image = image_factory.reload_image(new_page_number=self.page_num)
        return convert_to_png(new_image, 'image_factory_image.png')
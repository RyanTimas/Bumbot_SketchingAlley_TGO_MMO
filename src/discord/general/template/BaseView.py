import asyncio
import discord

from src.commons.CommonFunctions import convert_to_png, interaction_guard, retry_on_ssl_error
from src.commons.Modals.ChangeUserModal import ChangeUserModal
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
        self.is_server_view = target_user.user_id == 0

        self.interaction_lock = asyncio.Lock()

        # BUTTONS
        self.page_jump_dropdown = self.create_page_jump_dropdown(row=0)
        self.prev_button = self.create_navigation_button(is_next=False, row=1)
        self.next_button = self.create_navigation_button(is_next=True, row=1)

        self.go_back_button = self.create_go_back_button(row=4)
        self.close_button = self.create_close_button(row=4, )
        self.change_user_button = self.create_change_user_button(row=4)
        self.server_view_button = self.create_server_view_button(row=4)

    # BUTTONS
    def create_navigation_button(self, is_next, callback_func=None, row=0, disabled=False):
        button = discord.ui.Button(label="To Next Page➡️" if is_next else "⬅️To Previous Page", style=discord.ButtonStyle.blurple, row=row, disabled=disabled)
        button.callback = callback_func if callback_func else self.navigation_button_callback(is_next)
        return button
    def navigation_button_callback(self, is_next):
        @interaction_guard(self)
        async def callback(interaction):
            new_page_number = self.image_factory.page_num + (1 if is_next else -1)

            reloaded_image = self.reload_image(new_page_number=new_page_number)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback

    def create_go_back_button(self, row=4):
        button = discord.ui.Button(label="⬅️ Go Back", style=discord.ButtonStyle.red, row=row)
        button.callback = self.go_back_callback()
        return button
    def go_back_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            self.original_view.refresh_view()

            reloaded_image = self.original_view.reload_image()
            await interaction.message.edit(attachments=[reloaded_image] if reloaded_image else [], view=self.original_view)
        return callback

    def create_close_button(self, row=1):
        button = discord.ui.Button(label="✘", style=discord.ButtonStyle.red, row=row)
        button.callback = self.close_button_callback()
        return button
    def close_button_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            await interaction.message.delete()
        return callback

    def create_change_user_button(self, row=4):
        button = discord.ui.Button(label="👤 Change Display Player", style=discord.ButtonStyle.red, row=row)
        button.callback = self.change_user_callback()
        return button
    def change_user_callback(self):
        @interaction_guard(self, defer_response=False)
        async def callback(interaction):
            modal = ChangeUserModal(self)
            await interaction.response.send_modal(modal)
        return callback

    def create_server_view_button(self, row=4):
        button = discord.ui.Button(label="🌐 Server View", style=discord.ButtonStyle.green if self.is_server_view else discord.ButtonStyle.red, row=row)
        button.callback = self.server_view_callback()
        return button

    def server_view_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
            self.is_server_view = not self.is_server_view

            reloaded_image = self.reload_image(target_user=get_tgommo_db_handler().get_user_profile_by_user_id(0 if self.is_server_view else self.message_author.user_id))
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
        @interaction_guard(self)
        async def callback(interaction):
            new_page_number = int(interaction.data["values"][0])

            reloaded_image = self.reload_image(new_page_number=new_page_number)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback
    def update_page_jump_dropdown_options(self, active_img_factory):
        # Clear existing options and add new ones based on active factory
        self.page_jump_dropdown.options = []
        for page in range(1, active_img_factory.total_pages + 1):
            self.page_jump_dropdown.options.append(
                discord.SelectOption(
                    label=f"Page {page}",
                    value=str(page),
                    default=(page == active_img_factory.page_num)
                )
            )

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

        # update style
        self.server_view_button.style = discord.ButtonStyle.green if self.is_server_view else discord.ButtonStyle.red

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
        self.add_item(self.change_user_button)

    def reload_image(self, target_user= None, image_factory= None, new_page_number=None):
        image_factory =  image_factory if image_factory else self.image_factory
        new_image = image_factory.reload_image(target_user=target_user, new_page_number=self.page_num)
        return new_image if new_image is None else convert_to_png(new_image, 'image_factory_image.png')
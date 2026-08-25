# python
from math import ceil

from src.commons.CommonDecorators import interaction_guard
from src.discord.game_features.avatar_board.AvatarChangeImageFactory import AvatarChangeImageFactory
from src.discord.general.template.BaseView import BaseView

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
import discord

class AvatarChangeView(BaseView):
    def __init__(self, message_author, original_view, unlocked_avatars=None):
        # load unlocked avatars for the target user
        self.unlocked_avatars = unlocked_avatars if unlocked_avatars else get_tgommo_db_handler().get_unlocked_avatars_by_user_id(message_author.user_id) or []
        self.selected_avatar_id = message_author.avatar.avatar_id

        # load the image factory for the avatar change view, which will handle generating the image to display
        change_avatar_image_factory = AvatarChangeImageFactory(message_author=message_author, target_user=message_author)
        change_avatar_image_factory.total_pages = max(1, ceil(len(self.unlocked_avatars) / 25))

        super().__init__(message_author=message_author, target_user=message_author, image_factory=change_avatar_image_factory, original_view=original_view)

        # dropdown created with placeholder options; options updated in update_view_items()
        self.avatar_dropdown = self.create_avatar_dropdown(row=1)
        self.confirm_button = self.create_confirm_button(callback_func=self.confirm_button_callback(), row=2)

        self.page_jump_dropdown.placeholder = f"Page {self.page_num} of {self.image_factory.total_pages}"


        # Build initial state and UI
        self.refresh_view()

    '''----BUTTONS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def create_confirm_button(self, callback_func=None, row=2):
        button = discord.ui.Button(label="Change Avatar", style=discord.ButtonStyle.blurple, row=row)
        button.callback = callback_func if callback_func else self.navigation_button_callback()
        return button
    def confirm_button_callback(self):
        async def callback(interaction):
            # perform basic checks to ensure the user can change the avatar
            if not self.selected_avatar_id:
                await interaction.response.send_message("No avatar selected.", ephemeral=True)
                return
            if self.message_author.avatar.avatar_id == self.selected_avatar_id:
                await interaction.response.send_message("Selected avatar is the same as the current avatar.", ephemeral=True)
                return


            # update the user's profile display avatar in the database
            avatar_id = self.selected_avatar_id
            get_tgommo_db_handler().update_user_profile_display_avatar(user_id=self.target_user.user_id, avatar_id=avatar_id)
            new_avatar = get_tgommo_db_handler().get_avatar_by_id(avatar_id)

            self.original_view.message_author.Avatar = new_avatar
            self.original_view.target_user.Avatar = new_avatar
            self.target_user.Avatar = get_tgommo_db_handler().get_avatar_by_id(avatar_id)

            self.original_view.refresh_view()
            self.refresh_view()

            await interaction.response.send_message("Avatar changed.", files=new_avatar.avatar_image ,ephemeral=True)
        return callback

    '''----DROPDOWNS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def create_avatar_dropdown(self, row=0):
        dropdown = discord.ui.Select(placeholder="🚻 Select an Avatar", options=self.get_avatar_dropdown_options(), min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback()
        return dropdown
    def avatar_dropdown_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            self.selected_avatar_id = interaction.data["values"][0] if interaction.data and "values" in interaction.data and interaction.data["values"] else None

            # todo: add an image factory showing the available avatars for the selected avatar type, and update the view to show that image
            # reloaded_image = self.image_factory.build_image()
            # self.refresh_view()
            # await interaction.message.edit(attachments=[reloaded_image], view=self)
        return callback

    '''----SUPPORT FUNCTIONS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    # update the dropdown options to show the avatars for the current page of unlocked avatars
    def get_avatar_dropdown_options(self):
        # update dropdown options based on the current page of unlocked avatars
        small_end = (self.page_num - 1) * 25
        high_end = min(small_end + 25, len(self.unlocked_avatars))

        options = [discord.SelectOption(label=f"{avatar.name}", description=f"{avatar.series}", value=str(avatar.avatar_id)) for avatar in self.unlocked_avatars[small_end:high_end]]
        return options


    '''----UPDATE VIEW STATE------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def refresh_view(self):
        self.update_view_items()
        self.rebuild_view()
    def update_view_items(self):
        self.avatar_dropdown.options = self.get_avatar_dropdown_options()

        # keep select default selection in sync
        self.avatar_dropdown.label = f"Selected Avatar: {get_tgommo_db_handler().get_avatar_by_id(avatar_id=self.selected_avatar_id).name}" if self.selected_avatar_id else "🚻 Select an Avatar"

        if self.selected_avatar_id and any(opt.value == self.selected_avatar_id for opt in self.avatar_dropdown.options):
            self.avatar_dropdown.default_values = [self.selected_avatar_id]
        else:
            self.avatar_dropdown.default_values = [self.avatar_dropdown.options[0].value]
            self.selected_avatar_id = self.avatar_dropdown.options[0].value
    def rebuild_view(self):
        self.clear_items()

        self.add_item(self.page_jump_dropdown)
        self.add_item(self.avatar_dropdown)
        self.add_item(self.confirm_button)



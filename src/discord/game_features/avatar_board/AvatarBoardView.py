import discord

from src.commons.CommonFunctions import retry_on_ssl_error, convert_to_png, \
    interaction_guard
from src.zz_deprecated.AvatarBoardImageFactory import AVATAR_QUESTS, \
    UNLOCKED_AVATARS
from src.discord.general.template.BaseView import BaseView


class AvatarBoardView(BaseView):
    def __init__(self, message_author, target_user, avatar_board_unlocked_avatar_image_factory, avatar_board_quest_image_factory, open_tab=UNLOCKED_AVATARS, original_view=None):
        super().__init__(message_author=message_author, target_user=target_user, image_factory=None, original_view=original_view)

        self.open_tab = open_tab

        self.avatar_board_unlocked_avatar_image_factory = avatar_board_unlocked_avatar_image_factory
        self.avatar_board_quest_image_factory = avatar_board_quest_image_factory

        self.avatar_quests_button = self.create_open_avatar_quests_panel_button(row=2)
        self.unlocked_avatar_tab_button = self.create_open_unlocked_avatars_panel_button(row=2)

        self.refresh_view()

    def navigation_button_callback(self, is_next):
        @interaction_guard(self)
        async def callback(interaction):
            image_factory = self.avatar_board_unlocked_avatar_image_factory if self.open_tab == UNLOCKED_AVATARS else self.avatar_board_quest_image_factory
            new_page_number = image_factory.page_num + (1 if is_next else -1)

            reloaded_image = self.reload_image(new_page_number=new_page_number)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)

        return callback

    def create_open_unlocked_avatars_panel_button(self, row=1):
        button = discord.ui.Button(label="Unlocked Avatars", style=discord.ButtonStyle.primary, row=row)
        button.callback = self.open__unlocked_avatars_panel_callback()
        return button
    def open__unlocked_avatars_panel_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            self.open_tab = UNLOCKED_AVATARS

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def create_open_avatar_quests_panel_button(self, row=1):
        button = discord.ui.Button(label="Avatar Quests", style=discord.ButtonStyle.primary, row=row)
        button.callback = self.open_avatar_quests_panel_callback()
        return button
    def open_avatar_quests_panel_callback(self):
        @interaction_guard(self)
        @retry_on_ssl_error()
        async def callback(interaction):
            self.open_tab = AVATAR_QUESTS

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        active_img_factory = self.avatar_board_unlocked_avatar_image_factory if self.open_tab == UNLOCKED_AVATARS else self.avatar_board_quest_image_factory

        self.prev_button.disabled = active_img_factory.page_num == 1
        self.next_button.disabled = active_img_factory.page_num == active_img_factory.total_pages

        self.unlocked_avatar_tab_button.style = discord.ButtonStyle.green if self.open_tab == UNLOCKED_AVATARS else discord.ButtonStyle.gray
        self.avatar_quests_button.style = discord.ButtonStyle.green if self.open_tab == AVATAR_QUESTS else discord.ButtonStyle.gray

        self.update_page_jump_dropdown_options(active_img_factory=self.avatar_board_unlocked_avatar_image_factory if self.open_tab == UNLOCKED_AVATARS else self.avatar_board_quest_image_factory)  # Add this line

    def rebuild_view(self):
        self.clear_items()

        if (len(self.avatar_board_unlocked_avatar_image_factory.unlocked_avatars) > 75 and self.open_tab == UNLOCKED_AVATARS) or (len(self.avatar_board_quest_image_factory.avatar_quests) > 16 and self.open_tab == AVATAR_QUESTS):
            self.add_item(self.page_jump_dropdown)
            self.add_item(self.prev_button)
            self.add_item(self.next_button)

        self.add_item(self.unlocked_avatar_tab_button)
        self.add_item(self.avatar_quests_button)

        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)

    def reload_image(self, image_factory= None, new_page_number=None):
        image_factory = self.avatar_board_unlocked_avatar_image_factory if self.open_tab == UNLOCKED_AVATARS else self.avatar_board_quest_image_factory
        new_image = image_factory.reload_image(new_page_number=new_page_number)
        return convert_to_png(new_image, 'avatar_board_image.png')

    # SUPPORT FUNCTIONS


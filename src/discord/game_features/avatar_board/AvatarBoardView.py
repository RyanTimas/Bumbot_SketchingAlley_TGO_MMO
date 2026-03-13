import discord

from src.commons.CommonFunctions import retry_on_ssl_error, convert_to_png, interaction_guard
from src.discord.game_features.avatar_board import AvatarBoardImageFactory
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.TGO_MMO_constants import AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY, AVATAR_INVENTORY_QUEST_TAB_KEY


class AvatarBoardView(BaseView):
    def __init__(self, message_author, target_user, avatar_board_image_factory:AvatarBoardImageFactory, open_tab=AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY, original_view=None):
        super().__init__(message_author=message_author, target_user=target_user, image_factory=avatar_board_image_factory, original_view=original_view)
        self.open_tab = open_tab

        self.avatar_quests_button = self.create_open_avatar_quests_panel_button(row=2)
        self.unlocked_avatar_tab_button = self.create_open_unlocked_avatars_panel_button(row=2)

        self.refresh_view()

    def navigation_button_callback(self, is_next):
        @interaction_guard(self)
        async def callback(interaction):
            new_page_number = self.image_factory.get_page_num() + (1 if is_next else -1)

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
            self.open_tab = AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image(open_tab=AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY)], view=self)
        return callback

    def create_open_avatar_quests_panel_button(self, row=1):
        button = discord.ui.Button(label="Avatar Quests", style=discord.ButtonStyle.primary, row=row)
        button.callback = self.open_avatar_quests_panel_callback()
        return button
    def open_avatar_quests_panel_callback(self):
        @interaction_guard(self)
        @retry_on_ssl_error()
        async def callback(interaction):
            self.open_tab = AVATAR_INVENTORY_QUEST_TAB_KEY

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image(open_tab=AVATAR_INVENTORY_QUEST_TAB_KEY)], view=self)
        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.image_factory.open_tab = self.open_tab

        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        self.prev_button.disabled = self.image_factory.get_page_num() == 1
        self.next_button.disabled = self.image_factory.get_page_num() == self.image_factory.get_total_pages()

        self.unlocked_avatar_tab_button.style = discord.ButtonStyle.green if self.open_tab == AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY else discord.ButtonStyle.gray
        self.avatar_quests_button.style = discord.ButtonStyle.green if self.open_tab == AVATAR_INVENTORY_QUEST_TAB_KEY else discord.ButtonStyle.gray

        self.update_page_jump_dropdown_options(active_img_factory=self.image_factory.get_active_image_factory())  # Add this line

    def rebuild_view(self):
        self.clear_items()

        if (len(self.image_factory.avatar_board_unlocked_avatar_image_factory.unlocked_avatars) > 75 and self.open_tab == AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY) or (len(self.image_factory.avatar_board_quest_image_factory.avatar_quests) > 16 and self.open_tab == AVATAR_INVENTORY_QUEST_TAB_KEY):
            self.add_item(self.page_jump_dropdown)
            self.add_item(self.prev_button)
            self.add_item(self.next_button)

        self.add_item(self.unlocked_avatar_tab_button)
        self.add_item(self.avatar_quests_button)

        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)
        self.add_item(self.change_user_button)

    def reload_image(self, target_user= None, image_factory= None, new_page_number=None, open_tab=None):
        new_image = self.image_factory.reload_image(target_user=target_user, new_page_number=new_page_number, open_tab=open_tab)
        return convert_to_png(new_image, 'avatar_board_image.png')


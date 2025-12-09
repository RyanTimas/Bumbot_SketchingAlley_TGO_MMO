import asyncio

import discord

from src.commons.CommonFunctions import retry_on_ssl_error, check_if_user_can_interact_with_view, convert_to_png, \
    create_go_back_button, create_close_button
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous
from src.discord.game_features.avatar_board.AvatarBoardImageFactory import AvatarBoardImageFactory, AVATAR_QUESTS, \
    UNLOCKED_AVATARS


class AvatarBoardView(discord.ui.View):
    def __init__(self, message_author, avatar_board_image_factory: AvatarBoardImageFactory, open_tab=AVATAR_QUESTS, original_view=None):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.interaction_lock = asyncio.Lock()
        self.original_view = original_view

        self.avatar_board_image_factory = avatar_board_image_factory
        self.open_tab = open_tab

        self.open_unlocked_avatars_page = 1
        self.open_avatar_quests_page = 1

        self.prev_button = self.create_navigation_button(is_next=False, row=0)
        self.next_button = self.create_navigation_button(is_next=True, row=0)

        self.avatar_quests_button = self.create_open_avatar_quests_panel_button(row=1)
        self.unlocked_avatar_tab_button = self.create_open_unlocked_avatars_panel_button(row=1)

        self.go_back_button = create_go_back_button(original_view=self.original_view, row=2, interaction_lock=self.interaction_lock, message_author_id=self.message_author.id)
        self.close_button = create_close_button(row=2, interaction_lock=self.interaction_lock, message_author_id=self.message_author.id)

        self.refresh_view()


    def create_navigation_button(self, is_next, row=0):
        button = discord.ui.Button(
            label="To Next Page➡️" if is_next else "⬅️To Previous Page",
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.nav_callback(new_page=next_ if is_next else previous)
        return button
    def nav_callback(self, new_page,):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                # Update page number
                page_offset = -1 if new_page == previous else 1
                if self.open_tab == AVATAR_QUESTS:
                    self.avatar_board_image_factory.page_num_avatar_quests += page_offset
                elif self.open_tab == UNLOCKED_AVATARS:
                    self.avatar_board_image_factory.page_num_unlocked_avatar += page_offset

                new_image = self.avatar_board_image_factory.build_avatar_board_page_image()

                # Update state and button appearance
                self.refresh_view()

                # Send updated view
                file = convert_to_png(new_image, f'avatar_board_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def create_open_unlocked_avatars_panel_button(self, row=1):
        button = discord.ui.Button(
            label="Unlocked Avatars",
            style=discord.ButtonStyle.primary,
            row=row  # Place in second row
        )
        button.callback = self.open__unlocked_avatars_panel_callback()
        return button
    def open__unlocked_avatars_panel_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                new_image = self.avatar_board_image_factory.build_avatar_board_page_image(open_tab=UNLOCKED_AVATARS)
                self.open_tab = UNLOCKED_AVATARS
                self.refresh_view()

                # Send updated view
                file = convert_to_png(new_image, f'player_profile_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def create_open_avatar_quests_panel_button(self, row=1):
        button = discord.ui.Button(
            label="Avatar Quests",
            style=discord.ButtonStyle.primary,
            row=row  # Place in second row
        )
        button.callback = self.open_avatar_quests_panel_callback()
        return button
    def open_avatar_quests_panel_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                new_image = self.avatar_board_image_factory.build_avatar_board_page_image(open_tab=AVATAR_QUESTS)
                self.open_tab = AVATAR_QUESTS
                self.refresh_view()

                # Send updated view
                file = convert_to_png(new_image, f'player_profile_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        quests_current_page = self.avatar_board_image_factory.page_num_avatar_quests
        unlocked_avatars_current_page = self.avatar_board_image_factory.page_num_unlocked_avatar
        quests_total_pages = self.avatar_board_image_factory.total_avatar_quest_pages
        unlocked_avatars_total_pages = self.avatar_board_image_factory.total_unlocked_avatar_pages

        self.prev_button.disabled = (quests_current_page == 1) if self.open_tab == AVATAR_QUESTS else (unlocked_avatars_current_page == 1)
        self.next_button.disabled = (quests_current_page == quests_total_pages) if self.open_tab == AVATAR_QUESTS else (unlocked_avatars_current_page == unlocked_avatars_total_pages)

        self.unlocked_avatar_tab_button.style = discord.ButtonStyle.green if self.open_tab == UNLOCKED_AVATARS else discord.ButtonStyle.gray
        self.avatar_quests_button.style = discord.ButtonStyle.green if self.open_tab == AVATAR_QUESTS else discord.ButtonStyle.gray
    def rebuild_view(self):
        self.clear_items()

        if (len(self.avatar_board_image_factory.unlocked_avatars) > 75 and self.open_tab == UNLOCKED_AVATARS) or (len(self.avatar_board_image_factory.avatar_quests) > 16 and self.open_tab == AVATAR_QUESTS):
            self.add_item(self.prev_button)
            self.add_item(self.next_button)

        self.add_item(self.unlocked_avatar_tab_button)
        self.add_item(self.avatar_quests_button)

        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)

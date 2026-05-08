import discord

from src.commons.CommonDecorators import interaction_guard
from src.commons.CommonFunctions import convert_to_png
from src.discord.game_features.avatar_board import AvatarBoardImageFactory
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.TGO_MMO_constants import *


class AvatarBoardView(BaseView):
    def __init__(self, message_author, target_user, avatar_board_image_factory:AvatarBoardImageFactory, open_tab=AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY, original_view=None):
        super().__init__(message_author=message_author, target_user=target_user, image_factory=avatar_board_image_factory, original_view=original_view)
        self.open_tab = open_tab

        # View state attributes
        self.order_type = AVATAR_BOARD_SORT_AVATAR_TYPE
        self.expanded_display = ORDER_EXPANSION_KEY

        self.order_type_options = {
            AVATAR_BOARD_SORT_ALPHABETICAL: "Alphabetically",
            AVATAR_BOARD_SORT_DEX_NO: "Dex No",
            AVATAR_BOARD_SORT_SERIES: "Series",
            AVATAR_BOARD_SORT_AVATAR_TYPE: "Type",
        }
        self.filter_type_options = {
            AVATAR_BOARD_FILTER_COMPLETED_QUESTS: "Completed Quests",
        }
        self.expanded_view_options = {
            FILTER_EXPANSION_KEY: "Display Filter Options",
            ORDER_EXPANSION_KEY: "Display Sort Options",
        }

        # UI Components
        # row 2
        self.open_tab_toggle_button = self.create_open_tab_toggle_button(row=2, open_tab=AVATAR_INVENTORY_QUEST_TAB_KEY)

        self.expand_order_options_button = self.create_options_expansion_button(row=2, button_type=ORDER_EXPANSION_KEY)
        self.expand_filter_options_button = self.create_options_expansion_button(row=2, button_type=FILTER_EXPANSION_KEY)

        # row 3A - Sorting Options
        self.order_alphabetically_button = self.create_order_button(row=3, button_type=AVATAR_BOARD_SORT_ALPHABETICAL)
        self.order_series_button = self.create_order_button(row=3, button_type=AVATAR_BOARD_SORT_SERIES)
        self.order_avatar_type_button = self.create_order_button(row=3, button_type=AVATAR_BOARD_SORT_AVATAR_TYPE)
        self.order_dex_no_button = self.create_order_button(row=3, button_type=AVATAR_BOARD_SORT_DEX_NO) # unused for now since dex no sorting is the same as avatar type sorting for avatars, but may be useful if implemented for avatar quests in the future

        # row 3B - Filtering Options
        self.filter_completed_quests_button = self.create_filter_button(row=3, button_type=AVATAR_BOARD_FILTER_COMPLETED_QUESTS)

        self.refresh_view()

    def navigation_button_callback(self, is_next):
        @interaction_guard(self)
        async def callback(interaction):
            new_page_number = self.image_factory.get_page_num() + (1 if is_next else -1)

            reloaded_image = self.reload_image(new_page_number=new_page_number)
            self.refresh_view()
            await interaction.message.edit(attachments=[reloaded_image], view=self)

        return callback

    def apply_filter_options(self, button_type):
        if button_type == AVATAR_BOARD_FILTER_COMPLETED_QUESTS:
            self.image_factory.avatar_board_quest_image_factory.display_completed_quests = not self.image_factory.avatar_board_quest_image_factory.display_completed_quests

    '''----BUTTONS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def create_open_tab_toggle_button(self, row=1, open_tab=AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY):
        button = discord.ui.Button(label=f"Open Tab: {"Unlocked Avatars" if open_tab == AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY else "Avatar Quests"}", style=discord.ButtonStyle.green, row=row)
        button.callback = self.avatar_board_panel_callback(open_tab=open_tab)
        return button
    def avatar_board_panel_callback(self, open_tab):
        @interaction_guard(self)
        async def callback(interaction):
            self.open_tab = AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY if self.open_tab == AVATAR_INVENTORY_QUEST_TAB_KEY else AVATAR_INVENTORY_QUEST_TAB_KEY

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.image_factory.open_tab = self.open_tab

        self.update_view_items()
        self.rebuild_view()
    def update_view_items(self):
        super().update_view_items()

        # Update component's titles/labels
        self.open_tab_toggle_button.label = f"Open Tab: {'Unlocked Avatars' if self.open_tab == AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY else 'Avatar Quests'}"

        # Update component's disabled states
        self.prev_button.disabled = self.image_factory.get_page_num() == 1
        self.next_button.disabled = self.image_factory.get_page_num() == self.image_factory.get_total_pages()

        # Update Component's styles
        self.expand_order_options_button.style = discord.ButtonStyle.blurple if self.expanded_display == ORDER_EXPANSION_KEY else discord.ButtonStyle.gray
        self.expand_filter_options_button.style = discord.ButtonStyle.blurple if self.expanded_display == FILTER_EXPANSION_KEY else discord.ButtonStyle.gray

        self.order_alphabetically_button.style = discord.ButtonStyle.green if self.image_factory.get_order_type() == AVATAR_BOARD_SORT_ALPHABETICAL else discord.ButtonStyle.gray
        self.order_dex_no_button.style = discord.ButtonStyle.green if self.image_factory.get_order_type() == AVATAR_BOARD_SORT_DEX_NO else discord.ButtonStyle.gray
        self.order_series_button.style = discord.ButtonStyle.green if self.image_factory.get_order_type() == AVATAR_BOARD_SORT_SERIES else discord.ButtonStyle.gray
        self.order_avatar_type_button.style = discord.ButtonStyle.green if self.image_factory.get_order_type() == AVATAR_BOARD_SORT_AVATAR_TYPE else discord.ButtonStyle.gray

        self.filter_completed_quests_button.style = discord.ButtonStyle.green if self.image_factory.avatar_board_quest_image_factory.display_completed_quests else discord.ButtonStyle.gray

        # Update component's options
        self.update_page_jump_dropdown_options(active_img_factory=self.image_factory.get_active_image_factory())
    def rebuild_view(self):
        self.clear_items()

        # add the navigation buttons only if there are enough items for more than one page
        if (len(self.image_factory.avatar_board_unlocked_avatar_image_factory.unlocked_avatars) > 75 and self.open_tab == AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY) or (len(self.image_factory.avatar_board_quest_image_factory.avatars_with_quests) > 16 and self.open_tab == AVATAR_INVENTORY_QUEST_TAB_KEY):
            self.add_item(self.page_jump_dropdown)
            self.add_item(self.prev_button)
            self.add_item(self.next_button)

        # row 1 - tab buttons
        self.add_item(self.open_tab_toggle_button)

        # Sorting / Filter Options - Unlocked Avatars Tab
        if self.open_tab == AVATAR_INVENTORY_UNLOCKED_AVATARS_TAB_KEY:
            self.add_item(self.expand_order_options_button)
            if self.expanded_display == ORDER_EXPANSION_KEY:
                self.add_item(self.ascending_order_button)
                self.add_item(self.order_avatar_type_button)
                self.add_item(self.order_alphabetically_button)
                self.add_item(self.order_series_button)
                # self.add_item(self.order_dex_no_button) # unused for now since dex no sorting is the same as avatar type sorting for avatars, but may be useful if implemented for avatar quests in the future
            elif self.expanded_display == FILTER_EXPANSION_KEY:
                # todo: add buttons to filter unlocked avatars by different criteria such as avatar type, series, or to show only favorited avatars
                pass

        # Sorting / Filter Options - Quests Tab
        elif self.open_tab == AVATAR_INVENTORY_QUEST_TAB_KEY:
            self.add_item(self.expand_filter_options_button)
            if self.expanded_display == ORDER_EXPANSION_KEY:
                # todo: add buttons to sort avatar quests by different criteria such as completion status, quest type, etc.
                pass
            elif self.expanded_display == FILTER_EXPANSION_KEY:
                self.add_item(self.exclusive_mode_button)
                self.add_item(self.filter_completed_quests_button)
                pass

        # row 5
        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)
        self.add_item(self.change_user_button)

    def reload_image(self, target_user= None, image_factory= None, new_page_number=None):
        new_image = self.image_factory.reload_image(target_user=target_user, new_page_number=new_page_number, open_tab=self.open_tab, order_type=self.order_type, is_ascending_order=self.is_ascending_order, is_exclusive_mode=self.is_exclusive_mode)
        return convert_to_png(new_image, 'avatar_board_image.png')


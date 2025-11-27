import asyncio

import discord
from discord.ui import Select

from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_user_db_handler, get_tgommo_db_handler
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.creature_inventory.CreatureInventoryManagementView import CreatureInventoryManagementView
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous, jump
from src.resources.constants.TGO_MMO_constants import *

MYTHIC_KEY = "mythic_only"
FAVORITE_KEY = "favorite_only"
NICKNAME_KEY = "nickname_only"

FILTER_EXPANSION_KEY = "filter_expansion"
ORDER_EXPANSION_KEY = "order_expansion"
CREATURE_MANAGEMENT_EXPANSION_KEY = "creature_management"

class CreatureInventoryView(discord.ui.View):
    def __init__(self, message_author, owner_id, creature_inventory_image_factory: CreatureInventoryImageFactory, original_view=None):
        super().__init__(timeout=None)
        self.message_author = message_author
        self.owner_id = owner_id

        self.creature_inventory_image_factory = creature_inventory_image_factory
        self.original_view = original_view

        self.interaction_lock = asyncio.Lock()
        self.new_box = 1

        self.show_only_mythics = False
        self.show_only_favorites = False
        self.show_only_nicknames = False
        self.order_type = CAUGHT_DATE_ORDER
        self.expanded_display = FILTER_EXPANSION_KEY
        self.is_exclusive_mode = False
        self.is_ascending_order = False

        self.ids_to_release = []
        self.ids_to_favorite = []

        self.select_all_enabled = True

        # DEFINE VIEW COMPONENTS
        # row 0
        self.box_jump_dropdown = self.create_box_jump_dropdown(row=0)

        # row 1
        self.prev_button = self.create_navigation_button(is_next=False, row=1)
        self.page_jump_button = self.create_advanced_navigation_button(row=1)
        self.next_button = self.create_navigation_button(is_next=True, row=1)

        # row 2
        self.expand_filter_options_button = self.create_options_expansion_button(row=2, button_type=FILTER_EXPANSION_KEY)
        self.expand_order_options_button = self.create_options_expansion_button(row=2, button_type=ORDER_EXPANSION_KEY)
        self.expand_creature_management_options_button = self.create_options_expansion_button(row=2, button_type=CREATURE_MANAGEMENT_EXPANSION_KEY)

        # row 3a
        self.exclusive_mode_button = self.create_exclusive_mode_button(row=3)
        self.show_only_mythics_button = self.create_filter_button(row=3, button_type=MYTHIC_KEY)
        self.show_only_favorites_button = self.create_filter_button(row=3, button_type=FAVORITE_KEY)
        self.show_only_nicknames_button = self.create_filter_button(row=3, button_type=NICKNAME_KEY)

        # row 3b
        self.ascending_order_button = self.create_ascending_order_button(row=3)
        self.order_alphabetically_button = self.create_order_button(row=3, button_type=ALPHABETICAL_ORDER)
        self.order_catch_date_button = self.create_order_button(row=3, button_type=DEX_NO_ORDER)
        self.order_dex_no_button = self.create_order_button(row=3, button_type=CAUGHT_DATE_ORDER)

        # row 3c
        self.release_button = self.create_creature_management_button(row=3, button_type=CREATURE_INVENTORY_MODE_RELEASE)
        self.favorite_button = self.create_creature_management_button(row=3, button_type=CREATURE_INVENTORY_MODE_FAVORITE)

        # row 4
        self.close_button = create_close_button(interaction_lock=self.interaction_lock, message_author_id=self.message_author.id, row=4)
        self.go_back_button = create_go_back_button(original_view=self.original_view, row=4, interaction_lock=self.interaction_lock, message_author_id=self.message_author.id)

        self.refresh_view()

    # CREATE BUTTONS
    def create_navigation_button(self, is_next, row=0):
        button = discord.ui.Button(
            label="To Next Page➡️" if is_next else "⬅️To Previous Page",
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.nav_callback(new_page=next_ if is_next else previous)
        return button
    def create_advanced_navigation_button(self, row):
        button = discord.ui.Button(
            label="⬆️ Jump To Page ⬆️️",
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.nav_callback(new_page=jump)
        return button
    def nav_callback(self, new_page, ):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                # Update page number
                page_options = {
                    next_: self.creature_inventory_image_factory.current_box_num + 1,
                    previous: self.creature_inventory_image_factory.current_box_num - 1,
                    jump: self.new_box
                }

                update_image = self.reload_image(new_box_number=page_options[new_page])
                self.refresh_view()
                await interaction.message.edit(attachments=[update_image], view=self)
        return callback

    def create_filter_button(self, row=2, button_type=MYTHIC_KEY):
        button_type_options = {
            MYTHIC_KEY: "✨ Mythics Only",
            FAVORITE_KEY: "❤️ Favorites Only",
            NICKNAME_KEY: "❗Nicknames Only"
        }

        button = discord.ui.Button(
            label=button_type_options[button_type],
            style=discord.ButtonStyle.gray,
            row=row
        )
        button.callback = self.filter_button_callback(button_type=button_type)
        return button
    def filter_button_callback(self, button_type, ):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                if button_type == MYTHIC_KEY:
                    self.show_only_mythics = not self.show_only_mythics
                elif button_type == FAVORITE_KEY:
                    self.show_only_favorites = not self.show_only_favorites
                elif button_type == NICKNAME_KEY:
                    self.show_only_nicknames = not self.show_only_nicknames

                updated_image = self.reload_image()
                self.refresh_view()
                await interaction.message.edit(attachments=[updated_image], view=self)

        return callback

    def create_order_button(self, row=2, button_type=CAUGHT_DATE_ORDER):
        button_type_options = {
            ALPHABETICAL_ORDER: "Alphabetically",
            DEX_NO_ORDER: "Dex Number",
            CAUGHT_DATE_ORDER: "Caught Date"
        }

        button = discord.ui.Button(
            label=button_type_options[button_type],
            style=discord.ButtonStyle.gray,
            row=row
        )
        button.callback = self.order_button_callback(button_type=button_type)
        return button
    def order_button_callback(self, button_type, ):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                self.order_type = button_type

                updated_image = self.reload_image()
                self.refresh_view()
                await interaction.message.edit(attachments=[updated_image], view=self)

        return callback

    def create_exclusive_mode_button(self, row=3):
        button = discord.ui.Button(
            label="❌" if self.is_exclusive_mode else "✅",
            style=discord.ButtonStyle.red if self.is_exclusive_mode else discord.ButtonStyle.green,
            row=row,
        )
        button.callback = self.exclusive_mode_button_callback()
        return button
    def exclusive_mode_button_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                self.is_exclusive_mode = not self.is_exclusive_mode

                updated_image = self.reload_image()
                self.refresh_view()
                await interaction.message.edit(attachments=[updated_image], view=self)

        return callback

    def create_ascending_order_button(self, row=3):
        button = discord.ui.Button(
            label="⬆️" if self.is_ascending_order else "⬇️",
            style=discord.ButtonStyle.green if self.is_ascending_order else discord.ButtonStyle.red,
            row=row,
        )
        button.callback = self.ascending_order_button_callback()
        return button
    def ascending_order_button_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                self.is_ascending_order = not self.is_ascending_order

                updated_image = self.reload_image()
                self.refresh_view()
                await interaction.message.edit(attachments=[updated_image], view=self)

        return callback

    def create_options_expansion_button(self, row=3, button_type=FILTER_EXPANSION_KEY):
        button_type_options = {
            FILTER_EXPANSION_KEY: "Filters",
            ORDER_EXPANSION_KEY: "Sort",
            CREATURE_MANAGEMENT_EXPANSION_KEY: "Creature Management",
        }

        button = discord.ui.Button(
            label=button_type_options[button_type],
            style=discord.ButtonStyle.gray,
            row=row
        )

        button.callback = self.options_expansion_button_callback(button_type=button_type)
        return button
    def options_expansion_button_callback(self, button_type, ):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with (self.interaction_lock):
                await interaction.response.defer()

                self.expanded_display = button_type

                updated_image = self.reload_image()
                self.refresh_view()
                await interaction.message.edit(attachments=[updated_image], view=self)
        return callback

    def create_creature_management_button(self, button_type, row=3, ):
        label = {
            CREATURE_INVENTORY_MODE_RELEASE: "Release Selected Creatures",
            CREATURE_INVENTORY_MODE_FAVORITE: "Favorite Selected Creatures"
        }

        button = discord.ui.Button(
            label=label[button_type],
            style=discord.ButtonStyle.blurple,
            row=row
        )
        button.callback = self.creature_management_button_callback(button_type)
        return button
    def creature_management_button_callback(self, button_type):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            async with self.interaction_lock:
                view = CreatureInventoryManagementView(
                    message_author=self.message_author,
                    mode=button_type,
                    creatures=self.creature_inventory_image_factory.filtered_creatures[self.creature_inventory_image_factory.starting_index:self.creature_inventory_image_factory.ending_index],
                    creature_inventory_image_factory=self.creature_inventory_image_factory,
                    original_message=interaction.message,
                    original_view=self,
                    select_all_enabled=self.select_all_enabled,

                    show_only_mythics=self.show_only_mythics,
                    show_only_favorites=self.show_only_favorites,
                    show_only_nicknames=self.show_only_nicknames,
                )

                box_is_empty = len(self.creature_inventory_image_factory.caught_creatures[self.creature_inventory_image_factory.starting_index:self.creature_inventory_image_factory.ending_index]) == 0
                await interaction.response.send_message(content=f"Select creatures to {button_type}:" if not box_is_empty else f"you have no creatures to {button_type} in this box.", view=view, ephemeral=True)
        return callback


    # CREATE DROPDOWNS
    def create_box_jump_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Box {i}", value=str(i)) for i in range(1, self.creature_inventory_image_factory.total_unlocked_box_num + 1)]
        dropdown = Select(placeholder="Skip to Box", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.creature_box_dropdown_callback
        return dropdown
    async def creature_box_dropdown_callback(self, interaction: discord.Interaction):
        self.new_box = int(interaction.data["values"][0])
        await interaction.response.defer()


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        # UPDATE ENABLED/DISABLED STATES
        self.prev_button.disabled = self.creature_inventory_image_factory.current_box_num <= 1
        self.next_button.disabled = self.creature_inventory_image_factory.current_box_num >= self.creature_inventory_image_factory.total_unlocked_box_num

        # UPDATE BUTTON LABELS
        self.exclusive_mode_button.label = "❌" if self.is_exclusive_mode else "✅"
        self.ascending_order_button.label = "⬆️" if self.is_ascending_order else "⬇️"

        # UPDATE BUTTON STYLES
        self.expand_order_options_button.style = discord.ButtonStyle.green if self.expanded_display == ORDER_EXPANSION_KEY else discord.ButtonStyle.gray
        self.expand_filter_options_button.style = discord.ButtonStyle.green if self.expanded_display == FILTER_EXPANSION_KEY else discord.ButtonStyle.gray
        self.expand_creature_management_options_button.style = discord.ButtonStyle.green if self.expanded_display == CREATURE_MANAGEMENT_EXPANSION_KEY else discord.ButtonStyle.gray

        self.exclusive_mode_button.style = discord.ButtonStyle.red if self.is_exclusive_mode else discord.ButtonStyle.green
        self.show_only_mythics_button.style = discord.ButtonStyle.green if self.show_only_mythics else discord.ButtonStyle.gray
        self.show_only_favorites_button.style = discord.ButtonStyle.green if self.show_only_favorites else discord.ButtonStyle.gray
        self.show_only_nicknames_button.style = discord.ButtonStyle.green if self.show_only_nicknames else discord.ButtonStyle.gray

        self.ascending_order_button.style = discord.ButtonStyle.green if self.is_ascending_order else discord.ButtonStyle.red
        self.order_alphabetically_button.style = discord.ButtonStyle.green if self.order_type == ALPHABETICAL_ORDER else discord.ButtonStyle.gray
        self.order_catch_date_button.style = discord.ButtonStyle.green if self.order_type == DEX_NO_ORDER else discord.ButtonStyle.gray
        self.order_dex_no_button.style = discord.ButtonStyle.green if self.order_type == CAUGHT_DATE_ORDER else discord.ButtonStyle.gray
    def rebuild_view(self):
        for item in self.children.copy():
            self.remove_item(item)

        # add always visible items
        # row 0
        self.add_item(self.box_jump_dropdown)
        # row 1
        self.add_item(self.prev_button)
        self.add_item(self.page_jump_button)
        self.add_item(self.next_button)
        # row 2
        self.add_item(self.expand_filter_options_button)
        self.add_item(self.expand_order_options_button)
        self.add_item(self.expand_creature_management_options_button)
        # row 3a
        if self.expanded_display == FILTER_EXPANSION_KEY:
            self.add_item(self.exclusive_mode_button)
            self.add_item(self.show_only_mythics_button)
            self.add_item(self.show_only_favorites_button)
            self.add_item(self.show_only_nicknames_button)
        # row 3b
        elif self.expanded_display == ORDER_EXPANSION_KEY:
            self.add_item(self.ascending_order_button)
            self.add_item(self.order_alphabetically_button)
            self.add_item(self.order_catch_date_button)
            self.add_item(self.order_dex_no_button)
        # row 3c
        elif self.expanded_display == CREATURE_MANAGEMENT_EXPANSION_KEY:
            self.add_item(self.release_button)
            self.add_item(self.favorite_button)
        # row 4
        self.add_item(self.close_button)
        if self.original_view is not None:
            self.add_item(self.go_back_button)


    # SUPPORT FUNCTIONS
    def reload_image(self, new_box_number=None):
        reload_icons = self.creature_inventory_image_factory.image_mode == CREATURE_INVENTORY_MODE_RELEASE
        new_image = self.creature_inventory_image_factory.get_creature_inventory_page_image(refresh_creatures= reload_icons,order_type=self.order_type, new_box_number=new_box_number, show_mythics_only=self.show_only_mythics, show_favorites_only=self.show_only_favorites, show_nicknames_only=self.show_only_nicknames, is_ascending_order=self.is_ascending_order, is_exclusive_mode=self.is_exclusive_mode, )
        return convert_to_png(new_image, f'player_boxes_page.png')

import asyncio

import discord
from discord.ui import Select

from src.commons.CommonFunctions import *
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous, jump
from src.resources.constants.TGO_MMO_constants import *

MYTHIC_KEY = "mythic_only"
FAVORITE_KEY = "favorite_only"
NICKNAME_KEY = "nickname_only"

FILTER_EXPANSION_KEY = "filter_expansion"
ORDER_EXPANSION_KEY = "order_expansion"

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

        # DEFINE VIEW COMPONENTS
        self.box_jump_dropdown = self.create_box_jump_dropdown(row=0)

        self.prev_button = self.create_navigation_button(is_next=False, row=1)
        self.page_jump_button = self.create_advanced_navigation_button(row=1)
        self.next_button = self.create_navigation_button(is_next=True, row=1)

        self.expand_filter_options_button = self.create_options_expansion_button(row=2, button_type=FILTER_EXPANSION_KEY)
        self.expand_order_options_button = self.create_options_expansion_button(row=2, button_type=ORDER_EXPANSION_KEY)

        self.show_only_mythics_button = self.create_filter_button(row=3, button_type=MYTHIC_KEY)
        self.show_only_favorites_button = self.create_filter_button(row=3, button_type=FAVORITE_KEY)
        self.show_only_nicknames_button = self.create_filter_button(row=3, button_type=NICKNAME_KEY)

        self.order_alphabetically_button = self.create_order_button(row=3, button_type=ALPHABETICAL_ORDER)
        self.order_catch_date_button = self.create_order_button(row=3, button_type=DEX_NO_ORDER)
        self.order_dex_no_button = self.create_order_button(row=3, button_type=CAUGHT_DATE_ORDER)

        self.close_button = self.create_close_button(row=4)
        self.go_back_button = create_go_back_button(original_view=self.original_view, row=4, interaction_lock=self.interaction_lock, message_author_id=self.message_author.id)

        # self.release_button = self.create_release_button(row=3)

        # ADD ITEMS TO VIEW
        # row 0
        self.add_item(self.box_jump_dropdown)
        # row 1
        self.add_item(self.prev_button)
        self.add_item(self.page_jump_button)
        self.add_item(self.next_button)
        # row 2
        self.add_item(self.expand_filter_options_button)
        self.add_item(self.expand_order_options_button)
        self.add_item(create_dummy_label_button(label_text="Inventory Management (Coming Soon 😏)", row=2))

        # row 3a
        if self.expanded_display == FILTER_EXPANSION_KEY:
            self.add_item(self.show_only_mythics_button)
            self.add_item(self.show_only_favorites_button)
            self.add_item(self.show_only_nicknames_button)
        # row 3b
        elif self.expanded_display == ORDER_EXPANSION_KEY:
            self.add_item(self.order_alphabetically_button)
            self.add_item(self.order_catch_date_button)
            self.add_item(self.order_dex_no_button)

        # row 4
        self.add_item(self.close_button)
        if self.original_view is not None:
            self.add_item(self.go_back_button)

        self.update_button_states()

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

                new_image = self.creature_inventory_image_factory.build_creature_inventory_page_image(new_box_number=page_options[new_page])

                # Update state and button appearance
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'player_boxes_page.png')
                await interaction.message.edit(attachments=[file], view=self)

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

                new_image = self.creature_inventory_image_factory.build_creature_inventory_page_image(order_type=self.order_type, show_mythics_only=self.show_only_mythics, show_favorites_only=self.show_only_favorites, show_nicknames_only=self.show_only_nicknames)

                # Update state and button appearance
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'player_boxes_page.png')
                await interaction.message.edit(attachments=[file], view=self)

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
                new_image = self.creature_inventory_image_factory.build_creature_inventory_page_image(order_type=self.order_type, show_mythics_only=self.show_only_mythics, show_favorites_only=self.show_only_favorites, show_nicknames_only=self.show_only_nicknames, )

                # Update state and button appearance
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'player_boxes_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def create_options_expansion_button(self, row=3, button_type=FILTER_EXPANSION_KEY):
        button_type_options = {
            FILTER_EXPANSION_KEY: "Filters",
            ORDER_EXPANSION_KEY: "Sort",
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
                new_image = self.creature_inventory_image_factory.build_creature_inventory_page_image(order_type=self.order_type, show_mythics_only=self.show_only_mythics, show_favorites_only=self.show_only_favorites, show_nicknames_only=self.show_only_nicknames, )

                # Update state and button appearance
                self.update_button_states()

                # Send updated view
                file = convert_to_png(new_image, f'player_boxes_page.png')
                await interaction.message.edit(attachments=[file], view=self)

        return callback

    def create_close_button(self, row=2):
        button = discord.ui.Button(
            label="✘",
            style=discord.ButtonStyle.red,
            row=row
        )
        button.callback = self.close_callback()
        return button
    def close_callback(self):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            # Check if we're already processing an interaction
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.message_author.id):
                return

            # For delete operation, we need a shorter lock
            async with self.interaction_lock:
                # Delete the message
                await interaction.message.delete()

        return callback


    # CREATE DROPDOWNS
    def create_box_jump_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"Box {i}", value=str(i)) for i in range(1, self.creature_inventory_image_factory.total_unlocked_box_num + 1)]
        dropdown = Select(placeholder="Skip to Box", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.avatar_dropdown_callback
        return dropdown

    async def avatar_dropdown_callback(self, interaction: discord.Interaction):
        self.new_box = int(interaction.data["values"][0])
        await interaction.response.defer()

    # FUNCTIONS FOR UPDATING VIEW STATE
    def update_button_states(self):
        # UPDATE ENABLED/DISABLED STATES
        self.prev_button.disabled = self.creature_inventory_image_factory.current_box_num <= 1
        self.next_button.disabled = self.creature_inventory_image_factory.current_box_num >= self.creature_inventory_image_factory.total_unlocked_box_num

        # UPDATE BUTTON STYLES
        self.expand_order_options_button.style = discord.ButtonStyle.green if self.expanded_display == ORDER_EXPANSION_KEY else discord.ButtonStyle.gray
        self.expand_filter_options_button.style = discord.ButtonStyle.green if self.expanded_display == FILTER_EXPANSION_KEY else discord.ButtonStyle.gray

        self.show_only_mythics_button.style = discord.ButtonStyle.green if self.show_only_mythics else discord.ButtonStyle.gray
        self.show_only_favorites_button.style = discord.ButtonStyle.green if self.show_only_favorites else discord.ButtonStyle.gray
        self.show_only_nicknames_button.style = discord.ButtonStyle.green if self.show_only_nicknames else discord.ButtonStyle.gray

        self.order_alphabetically_button.style = discord.ButtonStyle.green if self.order_type == ALPHABETICAL_ORDER else discord.ButtonStyle.gray
        self.order_catch_date_button.style = discord.ButtonStyle.green if self.order_type == DEX_NO_ORDER else discord.ButtonStyle.gray
        self.order_dex_no_button.style = discord.ButtonStyle.green if self.order_type == CAUGHT_DATE_ORDER else discord.ButtonStyle.gray

        # ADD/REMOVE ITEMS FROM VIEW
        self.remove_items_from_view()

        if self.expanded_display == FILTER_EXPANSION_KEY:
            self.add_item(self.show_only_mythics_button)
            self.add_item(self.show_only_favorites_button)
            self.add_item(self.show_only_nicknames_button)
        elif self.expanded_display == ORDER_EXPANSION_KEY:
            self.add_item(self.order_alphabetically_button)
            self.add_item(self.order_catch_date_button)
            self.add_item(self.order_dex_no_button)


    def remove_items_from_view(self):
        # remove order buttons
        self.remove_item(self.order_alphabetically_button)
        self.remove_item(self.order_catch_date_button)
        self.remove_item(self.order_dex_no_button)

        # remove filter buttons
        self.remove_item(self.show_only_mythics_button)
        self.remove_item(self.show_only_favorites_button)
        self.remove_item(self.show_only_nicknames_button)


    # FUNCTIONS FOR UPDATING DATABASE
    def get_released_creatures(self):
        return [creature for creature in self.creatures if creature.is_released]

    def release_creatures(self, creature_ids: list[int]):
        pass


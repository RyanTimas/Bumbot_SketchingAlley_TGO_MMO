import asyncio
from discord.ui import Select, Modal

from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_user_db_handler, get_tgommo_db_handler
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.creature_inventory.CreatureInventoryManagementView import CreatureInventoryManagementView
from src.discord.game_features.encyclopedia.EncyclopediaView import next_, previous, jump
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.TGO_MMO_constants import *


class CreatureInventoryView(BaseView):
    def __init__(self, message_author, target_user, creature_inventory_image_factory: CreatureInventoryImageFactory, original_view=None):
        super().__init__(message_author=message_author, target_user=target_user, image_factory=creature_inventory_image_factory, original_view=original_view)

        # FILTER/ORDER STATE
        self.show_only_mythics = False
        self.show_only_favorites = False
        self.show_only_nicknames = False
        self.order_type = CREATURE_NICKNAME_SORT_CAUGHT_DATE
        self.expanded_display = CREATURE_INVENTORY_FILTER_EXPANSION_KEY
        self.is_exclusive_mode = False
        self.is_ascending_order = False

        self.ids_to_release = []
        self.ids_to_favorite = []

        self.select_all_enabled = True

        # DEFINE VIEW COMPONENTS
        # row 1
        self.storage_expansion_button = self.create_storage_expansion_button(row=1)
        # row 2
        self.expand_filter_options_button = self.create_options_expansion_button(row=2, button_type=CREATURE_INVENTORY_FILTER_EXPANSION_KEY)
        self.expand_order_options_button = self.create_options_expansion_button(row=2, button_type=CREATURE_INVENTORY_ORDER_EXPANSION_KEY)
        self.expand_creature_management_options_button = self.create_options_expansion_button(row=2, button_type=CREATURE_INVENTORY_CREATURE_MANAGEMENT_EXPANSION_KEY)

        # row 3a
        self.exclusive_mode_button = self.create_exclusive_mode_button(row=3)
        self.show_only_mythics_button = self.create_filter_button(row=3, button_type=CREATURE_INVENTORY_FILTER_MYTHIC)
        self.show_only_favorites_button = self.create_filter_button(row=3, button_type=CREATURE_FAVORITE_FILTER_MYTHIC)
        self.show_only_nicknames_button = self.create_filter_button(row=3, button_type=CREATURE_NICKNAME_FILTER_MYTHIC)

        # row 3b
        self.ascending_order_button = self.create_ascending_order_button(row=3)
        self.order_alphabetically_button = self.create_order_button(row=3, button_type=CREATURE_NICKNAME_SORT_ALPHABETICAL)
        self.order_catch_date_button = self.create_order_button(row=3, button_type=CREATURE_NICKNAME_SORT_DEX_NO)
        self.order_dex_no_button = self.create_order_button(row=3, button_type=CREATURE_NICKNAME_SORT_CAUGHT_DATE)

        # row 3c
        self.release_button = self.create_creature_management_button(row=3, button_type=CREATURE_INVENTORY_MODE_RELEASE)
        self.favorite_button = self.create_creature_management_button(row=3, button_type=CREATURE_INVENTORY_MODE_FAVORITE)

        # row 4
        self.refresh_view()

    # CREATE BUTTONS
    def create_storage_expansion_button(self, row=0):
        button = discord.ui.Button(label="Expand Storage ➕", style=discord.ButtonStyle.green, row=row)
        button.callback = self.storage_expansion_callback()
        return button
    def storage_expansion_callback(self, ):
        @interaction_guard(self)
        async def callback(interaction):
            if self.image_factory.page_num + 1 > MAX_CREATURE_STORAGE_EXPANSIONS:
                await interaction.followup.send("Your Storage is maxed out. It cannot be expanded any further.", ephemeral=True)
            elif self.message_author.user_id == self.target_user.user_id:
                await interaction.followup.send(self.create_inventory_expansion_confirmation_modal())
                return
        return callback

    # todo: move to base view
    def create_filter_button(self, row=2, button_type=CREATURE_INVENTORY_FILTER_MYTHIC):
        button_type_options = {
            CREATURE_INVENTORY_FILTER_MYTHIC: "✨ Mythics Only",
            CREATURE_FAVORITE_FILTER_MYTHIC: "❤️ Favorites Only",
            CREATURE_NICKNAME_FILTER_MYTHIC: "❗Nicknames Only"
        }

        button = discord.ui.Button(label=button_type_options[button_type], style=discord.ButtonStyle.gray, row=row)
        button.callback = self.filter_button_callback(button_type=button_type)
        return button
    def filter_button_callback(self, button_type, ):
        @interaction_guard(self)
        async def callback(interaction):
            self.show_only_mythics = not self.show_only_mythics if button_type == CREATURE_INVENTORY_FILTER_MYTHIC else self.show_only_mythics
            self.show_only_favorites = not self.show_only_favorites if button_type == CREATURE_FAVORITE_FILTER_MYTHIC else self.show_only_favorites
            self.show_only_nicknames = not self.show_only_nicknames if button_type == CREATURE_NICKNAME_FILTER_MYTHIC else self.show_only_nicknames

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def create_order_button(self, row=2, button_type=CREATURE_NICKNAME_SORT_CAUGHT_DATE):
        button_type_options = {
            CREATURE_NICKNAME_SORT_ALPHABETICAL: "Alphabetically",
            CREATURE_NICKNAME_SORT_DEX_NO: "Dex Number",
            CREATURE_NICKNAME_SORT_CAUGHT_DATE: "Caught Date"
        }
        button = discord.ui.Button(label=button_type_options[button_type], style=discord.ButtonStyle.gray, row=row)

        button.callback = self.order_button_callback(button_type=button_type)
        return button
    def order_button_callback(self, button_type, ):
        @interaction_guard(self)
        async def callback(interaction):
            self.order_type = button_type

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def create_exclusive_mode_button(self, row=3):
        button = discord.ui.Button(label="❌" if self.is_exclusive_mode else "✅", style=discord.ButtonStyle.red if self.is_exclusive_mode else discord.ButtonStyle.green, row=row,)
        button.callback = self.exclusive_mode_button_callback()
        return button
    def exclusive_mode_button_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            self.is_exclusive_mode = not self.is_exclusive_mode

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def create_ascending_order_button(self, row=3):
        button = discord.ui.Button(label="⬆️" if self.is_ascending_order else "⬇️", style=discord.ButtonStyle.green if self.is_ascending_order else discord.ButtonStyle.red, row=row,)
        button.callback = self.ascending_order_button_callback()
        return button
    def ascending_order_button_callback(self):
        @interaction_guard(self)
        async def callback(interaction):
            self.is_ascending_order = not self.is_ascending_order

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def create_options_expansion_button(self, row=3, button_type=CREATURE_INVENTORY_FILTER_EXPANSION_KEY):
        button_type_options = {
            CREATURE_INVENTORY_FILTER_EXPANSION_KEY: "Filters",
            CREATURE_INVENTORY_ORDER_EXPANSION_KEY: "Sort",
            CREATURE_INVENTORY_CREATURE_MANAGEMENT_EXPANSION_KEY: "Creature Management",
        }
        button = discord.ui.Button(label=button_type_options[button_type], style=discord.ButtonStyle.gray, row=row)

        button.callback = self.options_expansion_button_callback(button_type=button_type)
        return button
    def options_expansion_button_callback(self, button_type, ):
        @interaction_guard(self)
        async def callback(interaction):
            self.expanded_display = button_type

            self.refresh_view()
            await interaction.message.edit(attachments=[self.reload_image()], view=self)
        return callback

    def create_creature_management_button(self, button_type, row=3, ):
        label = {
            CREATURE_INVENTORY_MODE_RELEASE: "Release Selected Creatures",
            CREATURE_INVENTORY_MODE_FAVORITE: "Favorite Selected Creatures"
        }
        button = discord.ui.Button(label=label[button_type], style=discord.ButtonStyle.blurple, row=row)

        button.callback = self.creature_management_button_callback(button_type)
        return button
    def creature_management_button_callback(self, button_type):
        @interaction_guard(self)
        async def callback(interaction):
            view = CreatureInventoryManagementView(message_author=self.message_author, mode=button_type, creatures=self.image_factory.filtered_creatures[self.image_factory.starting_index:self.image_factory.ending_index], creature_inventory_image_factory=self.image_factory,original_message=interaction.message, original_view=self, select_all_enabled=self.select_all_enabled, show_only_mythics=self.show_only_mythics, show_only_favorites=self.show_only_favorites, show_only_nicknames=self.show_only_nicknames,)

            box_is_empty = len(self.image_factory.caught_creatures[self.image_factory.starting_index:self.image_factory.ending_index]) == 0
            await interaction.followup.send(content=f"Select creatures to {button_type}:" if not box_is_empty else f"you have no creatures to {button_type} in this box.", view=view, ephemeral=True)
        return callback


    # CREATE MODALS
    def create_inventory_expansion_confirmation_modal(self):
        user_details_modal = Modal(title=f"You currently have {self.target_user.currency} coins")
        user_details_modal.add_item(discord.ui.TextInput(label=f"Expand Storage? It will cost {self.get_expansion_cost()}. ", placeholder="Type 'confirm' to expand your creature storage", required=True, max_length=8))

        user_details_modal.on_submit = self.inventory_expansion_confirmation_modal_submit_callback
        return user_details_modal
    async def inventory_expansion_confirmation_modal_submit_callback(self, interaction: discord.Interaction):
        if interaction.data['components'][0]['components'][0]['value'].lower() == 'confirm':
            if self.target_user.currency >= self.get_expansion_cost():
                # Update DB Values
                get_tgommo_db_handler().update_user_profile_available_items(user_id=self.message_author, item_id=ITEM_ID_CREATURE_INVENTORY_STORAGE_EXPANSION, new_amount=self.max_boxes + 1)
                get_tgommo_db_handler().update_user_profile_currency(user_id=self.message_author, new_currency=self.get_expansion_cost() * -1)

                # Update local values
                self.target_user.currency -= self.get_expansion_cost()
                self.image_factory.total_pages += 1

                # Refresh View
                self.refresh_view()
                await interaction.message.edit(attachments=[self.reload_image(new_page_number=self.image_factory.page_num)], view=self)
                await interaction.response.send_message("✅ Your creature storage has been expanded by 100 slots!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ You do not have enough coins to expand your creature storage.", ephemeral=True)
                return
        else:
            await interaction.response.send_message("Storage expansion cancelled.", ephemeral=True)
        pass


    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        super().update_view_items()

        # UPDATE ENABLED/DISABLED STATES

        # UPDATE BUTTON LABELS
        self.exclusive_mode_button.label = "❌" if self.is_exclusive_mode else "✅"
        self.ascending_order_button.label = "⬆️" if self.is_ascending_order else "⬇️"
        self.next_button.label = "To Next Page➡️" if self.image_factory.page_num < self.image_factory.total_pages else "To Next Page➡️"

        # UPDATE BUTTON STYLES
        self.expand_order_options_button.style = discord.ButtonStyle.green if self.expanded_display == CREATURE_INVENTORY_ORDER_EXPANSION_KEY else discord.ButtonStyle.gray
        self.expand_filter_options_button.style = discord.ButtonStyle.green if self.expanded_display == CREATURE_INVENTORY_FILTER_EXPANSION_KEY else discord.ButtonStyle.gray
        self.expand_creature_management_options_button.style = discord.ButtonStyle.green if self.expanded_display == CREATURE_INVENTORY_CREATURE_MANAGEMENT_EXPANSION_KEY else discord.ButtonStyle.gray

        self.exclusive_mode_button.style = discord.ButtonStyle.red if self.is_exclusive_mode else discord.ButtonStyle.green
        self.show_only_mythics_button.style = discord.ButtonStyle.green if self.show_only_mythics else discord.ButtonStyle.gray
        self.show_only_favorites_button.style = discord.ButtonStyle.green if self.show_only_favorites else discord.ButtonStyle.gray
        self.show_only_nicknames_button.style = discord.ButtonStyle.green if self.show_only_nicknames else discord.ButtonStyle.gray
        self.next_button.style = discord.ButtonStyle.blurple if self.image_factory.page_num < self.image_factory.total_pages else discord.ButtonStyle.green if self.message_author.user_id == self.target_user.user_id else discord.ButtonStyle.blurple

        self.ascending_order_button.style = discord.ButtonStyle.green if self.is_ascending_order else discord.ButtonStyle.red
        self.order_alphabetically_button.style = discord.ButtonStyle.green if self.order_type == CREATURE_NICKNAME_SORT_ALPHABETICAL else discord.ButtonStyle.gray
        self.order_catch_date_button.style = discord.ButtonStyle.green if self.order_type == CREATURE_NICKNAME_SORT_DEX_NO else discord.ButtonStyle.gray
        self.order_dex_no_button.style = discord.ButtonStyle.green if self.order_type == CREATURE_NICKNAME_SORT_CAUGHT_DATE else discord.ButtonStyle.gray
    def rebuild_view(self):
        self.clear_items()

        # row 1
        if self.image_factory and self.image_factory.total_pages > 1:
            self.add_item(self.page_jump_dropdown)
            self.add_item(self.prev_button)
            self.add_item(self.storage_expansion_button if self.image_factory.page_num == self.image_factory.total_pages and self.message_author.user_id == self.target_user.user_id else self.next_button)

        # row 2
        self.add_item(self.expand_filter_options_button)
        self.add_item(self.expand_order_options_button)

        if self.message_author.user_id == self.target_user.user_id:
            self.add_item(self.expand_creature_management_options_button)

        # row 3a
        if self.expanded_display == CREATURE_INVENTORY_FILTER_EXPANSION_KEY:
            self.add_item(self.exclusive_mode_button)
            self.add_item(self.show_only_mythics_button)
            self.add_item(self.show_only_favorites_button)
            self.add_item(self.show_only_nicknames_button)
        # row 3b
        elif self.expanded_display == CREATURE_INVENTORY_ORDER_EXPANSION_KEY:
            self.add_item(self.ascending_order_button)
            self.add_item(self.order_alphabetically_button)
            self.add_item(self.order_catch_date_button)
            self.add_item(self.order_dex_no_button)
        # row 3c
        elif self.expanded_display == CREATURE_INVENTORY_CREATURE_MANAGEMENT_EXPANSION_KEY:
            self.add_item(self.release_button)
            self.add_item(self.favorite_button)

        # row 4
        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)
        self.add_item(self.change_user_button)


    # SUPPORT FUNCTIONS
    def reload_image(self, target_user= None, image_factory= None, new_page_number=None):
        reload_icons = self.image_factory.image_mode == CREATURE_INVENTORY_MODE_RELEASE
        new_image = self.image_factory.reload_image(target_user=target_user, refresh_creatures= reload_icons, order_type=self.order_type, new_page_number=new_page_number, show_mythics_only=self.show_only_mythics, show_favorites_only=self.show_only_favorites, show_nicknames_only=self.show_only_nicknames, is_ascending_order=self.is_ascending_order, is_exclusive_mode=self.is_exclusive_mode, )
        return convert_to_png(new_image, f'player_boxes_page.png')

    def get_expansion_cost(self):
        already_purchased_expansions = self.image_factory.total_pages - BASE_CREATURE_STORAGE_EXPANSIONS
        return (already_purchased_expansions + 1) * CREATURE_STORAGE_EXPANSION_BASE_COST

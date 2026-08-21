from discord.ui import Select

from src.commons.CommonDecorators import interaction_guard
from src.commons.CommonFunctions import *
from src.discord.game_features.item_inventory import ItemInventoryImageFactory
from src.discord.handlers.ItemUseHandler.ItemUseHandler import ItemUseHandler
from src.discord.general.template.BaseView import BaseView
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class ItemInventoryView(BaseView):
    def __init__(self, discord_bot, message_author, target_user, item_inventory_image_factory: ItemInventoryImageFactory, original_view=None, original_message=None):
        super().__init__(message_author=message_author, target_user=target_user, image_factory=item_inventory_image_factory, original_view=original_view)
        self.discord_bot = discord_bot
        self.original_message = original_message

        self.item_use_handler = ItemUseHandler(channel=None, discord_bot=self.discord_bot, original_view=self)

        self.selected_item = None

        # DEFINE VIEW COMPONENTS
        self.inventory_section_dropdown = self.create_inventory_section_dropdown(row=0)
        self.item_select_dropdown = self.create_items_dropdown(row=1)

        self.use_item_button = self.create_use_item_button(row=2)
        self.use_item_confirm_button = self.create_use_item_confirm_button(row=2)
        self.inventory_section_toggle_button = self.create_inventory_section_toggle_button(row=2)

        self.refresh_view()


    # CREATE BUTTONS
    def create_use_item_button(self, row=1):
        button = discord.ui.Button(label="Use Item", style=discord.ButtonStyle.green, row=row)

        button.callback = self.use_item_callback()
        return button
    def use_item_callback(self,):
        @interaction_guard(self)
        async def callback(interaction):
            if not self.selected_item:
                await interaction.followup.send(content="Please select an item to use from the dropdown menu.", ephemeral=True)
                return
            elif self.selected_item.item_quantity == 0:
                await interaction.followup.send(content="You don't have any more of this item to use.", ephemeral=True)
                return

            self.original_message = interaction.message if not self.original_message else self.original_message

            confirmation_view = discord.ui.View(timeout=60).add_item(self.create_use_item_confirm_button())
            self.refresh_view()

            item_img = convert_to_png(Image.open(f"{ITEM_BASE}{self.selected_item.img_root}{IMAGE_FILE_EXTENSION}"), f'item_img.png')
            await interaction.followup.send(content=f"You have selected {self.selected_item.item_name} to use.\nYou have {self.selected_item.item_quantity} left. Are you sure you want to use one?", files=[item_img], view=confirmation_view, ephemeral=True)
        return callback

    def create_use_item_confirm_button(self, row=1):
        button = discord.ui.Button(label="Confirm Use Item", style=discord.ButtonStyle.red, row=row)

        button.callback = self.use_item_confirm_callback()
        return button
    def use_item_confirm_callback(self,):
        @interaction_guard(self)
        async def callback(interaction):
            self.item_use_handler.original_message = self.original_message
            await self.item_use_handler.use_item(user=self.target_user, item=self.selected_item, interaction=interaction)
        return callback

    def create_inventory_section_toggle_button(self, row=1):
        button = discord.ui.Button(label=f"{ITEM_INVENTORY_TABS.get(self.image_factory.active_tab).get("label")}", style=discord.ButtonStyle.blurple, row=row)
        button.callback = self.inventory_section_toggle_callback()
        return button
    def inventory_section_toggle_callback(self, ):
        @interaction_guard(self, defer_response=False)
        async def callback(interaction):
            keys = list(ITEM_INVENTORY_ICON_ORDER_MAP.keys())
            current_tab_index = keys.index(self.image_factory.active_tab)
            next_tab = keys[(current_tab_index + 1) % len(keys)]

            self.refresh_view()
            await interaction.response.edit_message(content=None, attachments=[self.reload_image(active_tab=next_tab)], view=self)

        return callback

    # CREATE DROPDOWNS
    def create_inventory_section_dropdown(self, row=1):
        options = [discord.SelectOption(label=data["label"], value=tab_id) for tab_id, data in ITEM_INVENTORY_TABS.items()]
        placeholder_label = ITEM_INVENTORY_TABS.get(self.image_factory.active_tab, {}).get("label", "Section")
        dropdown = Select(placeholder=f"Section -> {placeholder_label}", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.inventory_section_dropdown_callback
        return dropdown

    async def inventory_section_dropdown_callback(self, interaction: discord.Interaction):
        selected_tab_id = interaction.data["values"][0]  # this is the short id (e.g. "bait")
        # update active tab using the short id
        old_tab = self.image_factory.active_tab
        if selected_tab_id != old_tab:
            self.image_factory.active_tab = selected_tab_id
            new_page_number = 1
            self.page_num = new_page_number
            self.image_factory.page_num = new_page_number

        reloaded_image = self.reload_image(active_tab=selected_tab_id)
        self.refresh_view()
        await interaction.response.edit_message(content=None, attachments=[reloaded_image], view=self)


    def create_items_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"{item.item_name} - ({item.item_quantity} left)", value=item.item_id) for item in self.image_factory.active_items[0:min(24, len(self.image_factory.active_items))]]
        dropdown = Select(placeholder="Select Item to Use", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.items_dropdown_callback
        return dropdown
    async def items_dropdown_callback(self, interaction: discord.Interaction):
        selected_item_id = interaction.data["values"][0]
        for item in self.image_factory.user_items:
            if item.item_id == selected_item_id:
                self.selected_item = item
                break
        await interaction.response.defer()

    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self):
        self.update_button_states()
        self.rebuild_view()
    def update_button_states(self):
        # update labels
        self.inventory_section_toggle_button.label = f"{ITEM_INVENTORY_ICON_ORDER_MAP.get(self.image_factory.active_tab)}"
        self.inventory_section_dropdown.placeholder =f"🎒Open Section -> {ITEM_INVENTORY_TABS.get(self.image_factory.active_tab, {}).get("label", "")}"

        # update the item select dropdown to reflect the current items
        self.item_select_dropdown = self.create_items_dropdown(row=1)
        pass
    def rebuild_view(self):
        super().rebuild_view()

        if len(self.image_factory.user_items) > 0 and self.target_user.user_id == self.message_author.user_id:
            self.add_item(self.inventory_section_dropdown)
            self.add_item(self.item_select_dropdown)

            self.add_item(self.use_item_button)
            self.add_item(self.inventory_section_toggle_button)


    # SUPPORT FUNCTIONS
    def reload_image(self, target_user= None, image_factory= None, new_page_number=None, active_tab=None):
        new_image = self.image_factory.reload_image(target_user=target_user, active_tab=active_tab)
        return convert_to_png(new_image, f'item_inventory_page.png')

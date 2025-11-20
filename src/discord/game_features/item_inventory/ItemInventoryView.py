from discord.ui import Select

from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.item_inventory import ItemInventoryImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class ItemInventoryView(discord.ui.View):
    def __init__(self, command_user, target_user, item_inventory_image_factory: ItemInventoryImageFactory, original_view=None, original_message=None):
        super().__init__(timeout=None)
        self.command_user = command_user
        self.target_user = target_user

        self.item_inventory_image_factory = item_inventory_image_factory
        self.original_view = original_view
        self.original_message = original_message

        self.interaction_lock = asyncio.Lock()

        self.user_items = self.item_inventory_image_factory.user_items
        self.selected_item = None

        # DEFINE VIEW COMPONENTS
        self.item_select_dropdown = self.create_items_dropdown(row=0)
        self.use_item_button = self.create_use_item_button(row=1)
        self.use_item_confirm_button = self.create_use_item_confirm_button(row=1)
        self.close_button = self.create_close_button(row=2)

        self.refresh_view(view_mode=VIEW_WORKFLOW_STATE_INITIAL)

    # CREATE BUTTONS
    def create_use_item_button(self, row=1):
        button = discord.ui.Button(
            label="Use Item",
            style=discord.ButtonStyle.green,
            row=row
        )
        button.callback = self.use_item_callback()
        return button
    def use_item_callback(self,):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.command_user.user_id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                if not self.selected_item:
                    await interaction.followup.send(content="Please select an item to use from the dropdown menu.", ephemeral=True)
                    return
                elif self.selected_item.item_quantity == 0:
                    await interaction.followup.send(content="You don't have any more of this item to use.", ephemeral=True)
                    return

                self.original_message = interaction.message
                self.refresh_view(view_mode=VIEW_WORKFLOW_STATE_CONFIRMATION)
                self.reload_image()

                item_img = convert_to_png(Image.open(f"{ITEM_INVENTORY_ITEM_BASE}{self.selected_item.img_root}{IMAGE_FILE_EXTENSION}"), f'item_img.png')
                await interaction.followup.send(content=f"You have selected {self.selected_item.item_name} to use.\nYou have {self.selected_item.item_quantity} left. Are you sure you want to use one?", files=[item_img], view=self, ephemeral=True)
        return callback

    def create_use_item_confirm_button(self, row=1):
        button = discord.ui.Button(
            label="Confirm Use Item",
            style=discord.ButtonStyle.red,
            row=row
        )
        button.callback = self.use_item_confirm_callback()
        return button
    def use_item_confirm_callback(self,):
        @retry_on_ssl_error(max_retries=3, delay=1)
        async def callback(interaction):
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.target_user.user_id):
                return

            async with self.interaction_lock:
                await interaction.response.defer()

                get_tgommo_db_handler().update_user_profile_available_items(user_id=self.target_user.user_id, item_id=self.selected_item.item_id, new_amount=self.selected_item.item_quantity - 1)
                item_img = convert_to_png(Image.open(f"{ITEM_INVENTORY_ITEM_BASE}{self.selected_item.img_root}{IMAGE_FILE_EXTENSION}"), f'item_img.png')

                await interaction.channel.send(content=f"{self.target_user.nickname} has used {self.selected_item.item_name}.", files=[item_img])
                # todo: schedule message to show item has worn off after 30 mins

                await self.original_message.delete()
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
            if not await check_if_user_can_interact_with_view(interaction, self.interaction_lock, self.command_user.id):
                return

            # For delete operation, we need a shorter lock
            async with self.interaction_lock:
                # Delete the message
                await interaction.message.delete()

        return callback

    # CREATE DROPDOWNS
    def create_items_dropdown(self, row=1):
        options = [discord.SelectOption(label=f"{item.item_name} - ({item.item_quantity} left)", value=item.item_id) for item in self.item_inventory_image_factory.user_items[0:min(24, len(self.item_inventory_image_factory.user_items))]]
        dropdown = Select(placeholder="Select Item to Use", options=options, min_values=1, max_values=1, row=row)
        dropdown.callback = self.items_dropdown_callback
        return dropdown
    async def items_dropdown_callback(self, interaction: discord.Interaction):
        selected_item_id = interaction.data["values"][0]
        for item in self.item_inventory_image_factory.user_items:
            if item.item_id == selected_item_id:
                self.selected_item = item
                break
        await interaction.response.defer()

    # FUNCTIONS FOR UPDATING VIEW STATE
    def refresh_view(self, view_mode: str = None):
        self.update_button_states()
        self.rebuild_view(view_mode)
    def update_button_states(self):
        pass
    def rebuild_view(self, view_mode: str = None):
        for item in self.children.copy():
            self.remove_item(item)

        # add options that will always appear

        if view_mode == VIEW_WORKFLOW_STATE_INITIAL:
            if len(self.user_items) > 0:
                self.add_item(self.item_select_dropdown)
                self.add_item(self.use_item_button)
            self.add_item(self.close_button)
        if view_mode == VIEW_WORKFLOW_STATE_CONFIRMATION:
            self.add_item(self.use_item_confirm_button)


    # SUPPORT FUNCTIONS
    def reload_image(self):
        new_image = self.item_inventory_image_factory.generate_item_inventory_image()
        return convert_to_png(new_image, f'item_inventory_page.png')

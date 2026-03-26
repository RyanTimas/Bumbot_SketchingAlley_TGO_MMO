import discord

from src.commons.CommonFunctions import convert_to_png, interaction_guard
from src.commons.CommonFunctions import retry_on_ssl_error
from src.commons.GameStateManager import get_game_state_manager
from src.discord.game_features.player_profile.PlayerProfileImageFactory import *
from src.discord.game_features.shop.ShopImageFactory import ShopImageFactory
from src.discord.general.template.BaseView import BaseView


class ShopView(BaseView):
    def __init__(self, message_author, shop_image_factory: ShopImageFactory, original_view=None):
        super().__init__(message_author=message_author, target_user=message_author, image_factory=shop_image_factory, original_view=original_view)

        self.selected_shop_item = None
        self.is_avatar_selected = False

        # DECLARE VIEW ITEMS
        self.shop_items_dropdown = self.create_shop_items_dropdown(row=0)
        self.buy_item_button = self.create_buy_item_button(row=1)

        # Add buttons to view
        super().refresh_view()

    ''' ----- VIEW COMPONENTS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''

    def create_buy_item_button(self, row=1):
        button = discord.ui.Button(label="Buy Item", style=discord.ButtonStyle.success, disabled=True, row=row)
        button.callback = self.buy_item_callback()
        return button
    def buy_item_callback(self):
        @interaction_guard()
        async def callback(interaction):
            if not self.selected_shop_item:
                await interaction.response.send_message("Please select an item first!", ephemeral=True)
                return

            confirmation_view = BuyConfirmationView(self.message_author, self.selected_shop_item, self.is_avatar_selected, self)

            item_type = "Avatar" if self.is_avatar_selected else "Item"
            await interaction.response.send_message(f"Are you sure you want to buy this {item_type}: {getattr(self.selected_shop_item, "name" if self.is_avatar_selected else "item_name")}?", view=confirmation_view, ephemeral=True)
        return callback

    def create_shop_items_dropdown(self, row=2):
        options = []

        # Add shop items
        if hasattr(self.image_factory, 'shop_items'):
            for item in self.image_factory.shop_items:
                options.append(discord.SelectOption(label=f"🎒Item: {item.item_name}", value=f"item_{item.item_id}", description=f"Price: {item.shop_price}"))

        # Add shop avatars
        if hasattr(self.image_factory, 'shop_avatars'):
            for avatar in self.image_factory.shop_avatars:
                options.append(discord.SelectOption(label=f"🚻Avatar: {avatar.name}", value=f"avatar_{avatar.avatar_id}",  description=f"Price: {avatar.shop_price}"))

        if not options:
            options.append(discord.SelectOption(label="No items available", value="none"))

        dropdown = discord.ui.Select(placeholder="Select an item to purchase...", options=options[:25], row=row)
        dropdown.callback = self.shop_item_select_callback()
        return dropdown

    def shop_item_select_callback(self):
        @interaction_guard()
        async def callback(interaction):
            await interaction.response.defer()
            selected_value = interaction.data['values'][0]

            self.is_avatar_selected = selected_value.startswith("avatar_")
            item_id = selected_value.replace("item_", "") if selected_value.startswith("item_") else selected_value.replace("avatar_", "")
            self.selected_shop_item = next((item for item in (self.image_factory.shop_avatars if self.is_avatar_selected else self.image_factory.shop_items) if getattr(item, 'avatar_id' if self.is_avatar_selected else 'item_id') == item_id), None)

            if self.is_avatar_selected:
                self.selected_shop_item = next((avatar for avatar in self.image_factory.shop_avatars if avatar.avatar_id == item_id), None)
            else:
                self.selected_shop_item = next((item for item in self.image_factory.shop_items if item.item_id == item_id), None)

            # Enable buy button
            self.update_view_items()

            # Update the view
            await interaction.edit_original_response(view=self)
        return callback
    ''' ----- SUPPORT FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def update_view_items(self):
        self.buy_item_button.disabled = not self.selected_shop_item
        self.shop_items_dropdown.placeholder = "Select an item to purchase..." if not self.selected_shop_item else f"{'🚻Avatar' if self.is_avatar_selected else '🎒Item'}: {self.selected_shop_item.name if self.is_avatar_selected else self.selected_shop_item.item_name} ({self.selected_shop_item.shop_price}💰)"

    def rebuild_view(self):
        self.clear_items()

        # row 0
        self.add_item(self.shop_items_dropdown)
        # row 1
        self.add_item(self.buy_item_button)

        # row 4
        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)

    def reload_image(self, target_user= None, image_factory= None, new_page_number=None):
        new_image = self.image_factory.reload_image()
        return convert_to_png(new_image, 'shop_image.png')


''' ----- SUPPORT CLASSES ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
class BuyConfirmationView(discord.ui.View):
    def __init__(self, message_author, selected_item, is_avatar, parent_view):
        super().__init__(timeout=60)
        self.message_author = message_author
        self.is_avatar = is_avatar
        self.purchased_item = get_tgommo_db_handler().get_avatar_by_id(avatar_id=selected_item.avatar_id) if is_avatar else get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=self.message_author.user_id, item_id=selected_item.item_id)
        self.parent_view = parent_view

        self.confirmation_button = self.create_confirm_purchase_button()
        self.add_item(self.confirmation_button)


    def create_confirm_purchase_button(self, row=1):
        button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.success, row=row)
        button.callback = self.confirm_purchase_callback()
        return button
    def confirm_purchase_callback(self):
        @interaction_guard()
        async def callback(interaction):
            # check to see if user has enough currency
            await interaction.response.defer()

            if self.message_author.currency < self.purchased_item.shop_price:
                await interaction.followup.send("You don't have enough currency to buy this item!", ephemeral=True)
                return

            # check to see if the user already owns the item (if it's an avatar)
            if self.is_avatar and get_tgommo_db_handler().has_user_unlocked_avatar(user_id=self.message_author.user_id, avatar_id=self.purchased_item.avatar_id):
                await interaction.followup.send("You already own this avatar!", ephemeral=True)
                return

            # check to see if user already purchased the item today (if it's a shop item)
            if not self.is_avatar and get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=self.message_author.user_id, item_id=self.purchased_item.item_id).last_purchase_date == get_game_state_manager().get_shop_date():
                await interaction.followup.send("You already bought this item today!", ephemeral=True)
                return

            # if they pass all checks, proceed with purchase - give the user the item/ avatar
            if self.is_avatar:
                get_tgommo_db_handler().insert_new_user_profile_avatar_link(avatar_id=self.purchased_item.avatar_id, user_id=self.message_author.user_id)
            else:
                get_tgommo_db_handler().update_user_profile_available_items(user_id=self.message_author.user_id, item_id=self.purchased_item.item_id, new_amount=self.purchased_item.item_quantity + 1)
                get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=self.message_author.user_id, item_id=self.purchased_item.item_id, last_purchased_date=get_game_state_manager().get_shop_date())

            # remove currency from user
            get_tgommo_db_handler().update_user_profile_currency(user_id=self.message_author.user_id, new_currency=self.message_author.currency - self.purchased_item.shop_price)

            await interaction.followup.send(f"Purchase confirmed! You bought the avatar: {self.purchased_item.name}!", file=convert_to_png(image=self.purchased_item.avatar_unlock_image, file_name="avatar.png") if self.is_avatar else None, ephemeral=True)
        return callback

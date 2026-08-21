from src.commons.CommonDecorators import interaction_guard
from src.commons.GameStateManager import get_game_state_manager, game_state_manager
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
        self.donate_button = self.create_donate_button(row=1)

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

            # generate confirmation message based on whether the selected item is an avatar or a shop item
            confirmation_view = BuyConfirmationView(self.message_author, self.selected_shop_item, self.is_avatar_selected, self, interaction.message)
            message = f"Are you sure you want to buy this {"Avatar" if self.is_avatar_selected else "Item"}: {getattr(self.selected_shop_item, 'name' if self.is_avatar_selected else 'item_name')} for {self.selected_shop_item.shop_price}💰?"
            await interaction.response.send_message(message, files=[convert_to_png(image=(getattr(self.selected_shop_item, 'avatar_image' if self.is_avatar_selected else 'item_image')), file_name="selected_item.png")], view=confirmation_view, ephemeral=True)
        return callback

    def create_donate_button(self, row=1):
        button = discord.ui.Button(label="Donate to Morshu", style=discord.ButtonStyle.primary, disabled=False, row=row)
        button.callback = self.donate_callback()
        return button
    def donate_callback(self):
        @interaction_guard()
        async def callback(interaction):
            # Open a modal to ask how much to donate
            modal = DonationModal(message_author=self.message_author, parent_view=self, original_message=interaction.message)
            await interaction.response.send_modal(modal)
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
        self.donate_button.disabled = (self.message_author.currency <= 0)
        self.shop_items_dropdown.placeholder = "Select an item to purchase..." if not self.selected_shop_item else f"{'🚻Avatar' if self.is_avatar_selected else '🎒Item'}: {self.selected_shop_item.name if self.is_avatar_selected else self.selected_shop_item.item_name} ({self.selected_shop_item.shop_price}💰)"

    def rebuild_view(self):
        self.clear_items()

        # row 0
        self.add_item(self.shop_items_dropdown)
        # row 1
        self.add_item(self.buy_item_button)
        self.add_item(self.donate_button)

        # row 4
        self.add_item(self.close_button)
        if self.original_view:
            self.add_item(self.go_back_button)

    def reload_image(self, target_user= None, image_factory= None, new_page_number=None):
        new_image = self.image_factory.reload_image()
        return convert_to_png(new_image, 'shop_image.png')


''' ----- SUPPORT CLASSES ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
class BuyConfirmationView(discord.ui.View):
    def __init__(self, message_author, selected_item, is_avatar, parent_view, original_message=None):
        super().__init__(timeout=60)
        self.message_author = message_author
        self.is_avatar = is_avatar
        self.purchased_item = get_tgommo_db_handler().get_avatar_by_id(avatar_id=selected_item.avatar_id) if is_avatar else get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=self.message_author.user_id, item_id=selected_item.item_id)
        self.parent_view = parent_view
        self.original_message = original_message

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
                users_item_total = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=self.message_author.user_id, item_id=self.purchased_item.item_id).item_quantity
                get_tgommo_db_handler().update_user_profile_available_items(user_id=self.message_author.user_id, item_id=self.purchased_item.item_id, new_amount=users_item_total + 1)
                get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=self.message_author.user_id, item_id=self.purchased_item.item_id, last_purchased_date=get_game_state_manager().get_shop_date())

            # remove currency from user
            get_tgommo_db_handler().update_user_profile_currency(user_id=self.message_author.user_id, new_currency=self.purchased_item.shop_price * -1)
            self.parent_view.image_factory.message_author.currency -= self.purchased_item.shop_price

            # Refresh the parent view with updated currency
            await self.original_message.edit(attachments=[self.parent_view.reload_image()], view=self.parent_view)

            message = f"Purchase confirmed! You bought the {"avatar" if self.is_avatar else "item"}: {getattr(self.purchased_item, "name" if self.is_avatar else "item_name")}!"
            await interaction.followup.send(message, file=convert_to_png(image=(getattr(self.purchased_item, ("avatar_unlock_image" if self.is_avatar else "item_unlock_image"))), file_name="purchased_shop_item.png"), ephemeral=True)
        return callback

class DonationModal(discord.ui.Modal):
    amount = discord.ui.TextInput(label="How much would you like to donate?", style=discord.TextStyle.short, placeholder="Enter amount", required=True, max_length=10)

    def __init__(self, message_author, parent_view: ShopView, original_message=None):
        super().__init__(title="Donate to Morshu")
        self.message_author = message_author
        self.parent_view = parent_view
        self.original_message = original_message

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        raw = self.amount.value.strip().replace(',', '')
        try:
            amount = int(raw)
        except ValueError:
            await interaction.followup.send("Please enter a valid whole number amount.", ephemeral=True)
            return

        if amount <= 0:
            await interaction.followup.send("Donation amount must be greater than zero.", ephemeral=True)
            return

        if self.message_author.currency < amount:
            await interaction.followup.send("You don't have enough currency to donate that amount.", ephemeral=True)
            return

        # Deduct currency from user (DB expects delta)
        get_tgommo_db_handler().update_user_profile_currency(user_id=self.message_author.user_id, new_currency=-amount)

        # Update local user cache
        if hasattr(self.parent_view.image_factory, 'message_author'):
            self.parent_view.image_factory.message_author.currency -= amount
        else:
            self.message_author.currency -= amount

        # Update global shop donation total and handle level ups
        gsm = get_game_state_manager()
        current_level = gsm.get_shop_level()
        donation_total = gsm.get_shop_donation_total() + amount

        leveled_up = False
        new_level = current_level

        # Support multiple level ups if donation exceeds multiple goals
        while True:
            donation_goal = SHOP_LEVEL_COST_MAP.get(new_level, max(SHOP_LEVEL_COST_MAP.values()))
            if donation_total < donation_goal:
                break
            donation_total -= donation_goal
            new_level += 1
            leveled_up = True

        gsm.set_shop_level(new_level)
        gsm.set_shop_donation_total(donation_total)

        if leveled_up:
            # Set the shop upgrade in progress flag if the new level is less than the max level
            gsm.set_shop_upgrade_in_progress(gsm.get_max_shop_level() > new_level)

            await interaction.followup.send(f"Thank you for your donation of {amount}💰! The shop has leveled up to Level {new_level}! New items may be available, so be sure to check back!",ephemeral=True)
            await interaction.followup.send(f"🎉 The shop has leveled up to Level {new_level}! 🎉", files=[convert_to_png(Image.open(SHOP_UPDATE_UPGRADE_IMAGE), file_name="shop_upgrade.png")], ephemeral=False)

        # Refresh the parent view image
        if self.original_message:
            await self.original_message.edit(attachments=[self.parent_view.reload_image()], view=self.parent_view)

        await interaction.followup.send(f"Thank you for donating {amount}💰 to Morshu!", ephemeral=True)
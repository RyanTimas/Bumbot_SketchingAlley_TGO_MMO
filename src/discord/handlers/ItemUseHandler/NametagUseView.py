import traceback

import discord
from discord.ui import View, Button, Modal

from src.commons.CommonFunctions import retry_on_ssl_error
from src.commons.CommonViewComponents import create_display_creature_collection_button
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.handlers.AvatarUnlockHandler.AvatarUnlockHandler import check_for_secret_avatars
from src.discord.objects import TGOPlayer
from src.resources.constants.TGO_MMO_constants import ITEM_ID_NAMETAG


class NametagUseView(View):
    def __init__(self, target_user: TGOPlayer, item_use_handler):
        super().__init__(timeout=300)
        self.target_user = target_user
        self.nametag_item = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=target_user.user_id, item_id=ITEM_ID_NAMETAG)
        self.item_use_handler = item_use_handler

        self.catch_id_input = discord.ui.TextInput(label='Creature Catch ID', placeholder='Enter the catch ID of the creature you want to rename...', required=True, max_length=10)
        self.new_nickname_input = discord.ui.TextInput(label='New Nickname', placeholder='Enter the new nickname for your creature...', required=True, max_length=20)

        self.add_item(self.create_rename_creature_button(row=0))
        self.add_item(create_display_creature_collection_button(user=target_user, row=0))

    '''----BUTTONS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def create_rename_creature_button(self, row=1):
        button = Button(label="Rename Creature", style=discord.ButtonStyle.green)
        button.callback = self.rename_creature_callback()
        return button
    def rename_creature_callback(self):
        @retry_on_ssl_error()
        async def callback(interaction):
            await interaction.response.send_modal(self.create_rename_creature_modal())
        return callback

    '''----MODALS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'''
    def create_rename_creature_modal(self):
        rename_creature_modal = Modal(title=f"Rename Your Creature")

        rename_creature_modal.add_item(self.catch_id_input)
        rename_creature_modal.add_item(self.new_nickname_input)

        rename_creature_modal.on_submit = self.rename_creature_modal_submit_callback
        return rename_creature_modal

    async def rename_creature_modal_submit_callback(self, interaction):
        try:
            catch_id = int(self.catch_id_input.value)

            # Verify the creature belongs to the user
            if not get_tgommo_db_handler().does_user_own_catch_id(user_id=self.target_user.user_id, catch_id=catch_id):
                await interaction.response.send_message(f"You don't own a creature with catch ID {catch_id}.", ephemeral=True)
                return

            creature = get_tgommo_db_handler().get_user_creature_by_catch_id(catch_id=catch_id)

            # Update the creature's nickname in the database
            get_tgommo_db_handler().update_creature_nickname(catch_id=catch_id, new_nickname=self.new_nickname_input.value)

            # remove 1 nametag from user's inventory
            get_tgommo_db_handler().update_user_profile_available_items(user_id=self.target_user.user_id, item_id=ITEM_ID_NAMETAG, new_amount=get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id( item_id=self.nametag_item.item_id, user_id=self.target_user.user_id).item_quantity - 1)
            self.nametag_item.item_quantity -= 1

            await interaction.response.send_message(f"Successfully renamed your creature {creature.nickname} to '{self.new_nickname_input.value}'!", ephemeral=True)
            await interaction.followup.send(f"<@{self.target_user.user_id}> ({self.target_user.nickname}) used a nametag to rename their creature!", files=[self.item_use_handler.get_image_for_item(self.nametag_item)])

            # Check if the new nickname has unlocked a new secret avatar
            await check_for_secret_avatars(user_id=interaction.user.id, nickname=self.new_nickname_input.value, interaction=interaction)
        except ValueError:
            await interaction.response.send_message("Please enter a valid numeric catch ID.", ephemeral=True)
        except Exception as e:
            print(f"Error in rename_creature_modal_submit_callback: {str(e)}")
            print(traceback.format_exc())
            await interaction.response.send_message(f"An error occurred while renaming your creature. You did not lose your Nametag. Reach out to Bumbiss for assistance.", ephemeral=True)

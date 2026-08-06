import datetime

import discord
import pytz

from src.commons.CommonFunctions import convert_to_png, convert_to_datetime
from src.commons.GameStateManager import get_game_state_manager
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.handlers.ItemUnlockHandler.ItemUnlockImageFactory import ItemUnlockImageFactory
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import TRAP_ID_RARITY_MAP, ITEM_ID_BASIC_TRAP, ITEM_ID_BATTERY
from src.resources.constants.file_paths import *

# check if player has unlocked any items from catching creature
async def check_for_milestone_catch_rewards(user_id, interaction):
    # if user has not unlocked the basic trap, grant them this item
    user_basic_trap = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP)
    if user_basic_trap.item_quantity == 0:
        # first load the player's trap link to ensure they have a trap link entry in the database
        get_tgommo_db_handler().get_player_trap_link_by_user_id(user_id=user_id)

        # next update the player's inventory to add the basic trap & when it was unlocked
        get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP, new_amount=1)
        get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP, last_purchased_date=int(datetime.datetime.now().timestamp()))

        # grant the user 3 batteries to start off with
        user_battery = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_BATTERY)
        get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_BATTERY, new_amount=user_battery.item_quantity + 3)
        get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP, last_purchased_date=int(datetime.datetime.now().timestamp()))

        # next, let the user know they have unlocked the basic trap and send them the image of the trap
        await interaction.followup.send(f"Congratulations! You've unlocked the Basic Trap!! You can use this to capture creatures while AFK. Check the Trap Manager to view your current trap configurations.", file=convert_to_png(image=user_basic_trap.item_unlock_image, file_name="basic_trap_unlock.png"), ephemeral=True)
        await interaction.followup.send(f"Congratulations! You've unlocked three batteries for unlocking the Basic Trap!! You can use these to charge your trap. Check the Trap Manager to charge your trap.", file=convert_to_png(image=user_battery.item_unlock_image, file_name="battery_unlock.png"), ephemeral=True)
    return
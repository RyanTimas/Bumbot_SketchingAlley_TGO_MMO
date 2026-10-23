import datetime
import random

from src.caching import resolve_static_content_cache
from src.caching.db_specific_caches.static_item_cache import StaticItemCache
from src.commons.CommonFunctions import convert_to_png
from src.commons.AsyncBlocking import run_serialized_blocking
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from resources.constants.TGO_MMO_constants import *

# region Milestone Unlocks
# check if player has unlocked any items from catching creature
async def check_for_milestone_catch_rewards(user_id, interaction):
    notifications = await run_serialized_blocking(_prepare_milestone_catch_notifications, user_id)
    for message, image in notifications:
        await interaction.followup.send(message, file=image, ephemeral=True)
def _prepare_milestone_catch_notifications(user_id):
    notifications = []
    notifications.extend(_unlock_basic_trap(user_id))
    return notifications

# region Individual Milestone Unlocks
def _unlock_basic_trap(user_id):
    # UNLOCK CONDITIONS: 100 creatures caught and user does not already have a basic trap
    user_catch_count = len(get_tgommo_db_handler().get_user_creatures_by_user_id(user_id=user_id))
    user_basic_trap = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP)
    if user_basic_trap.item_quantity >= 1 or user_catch_count < 100:
        return []

    # Unlock the basic trap, 3 batteries, and an omnipotent bait for the user
    get_tgommo_db_handler().get_player_trap_link_by_user_id(user_id=user_id)
    get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP, new_amount=1)
    get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP, last_purchased_date=int(datetime.datetime.now().timestamp()))

    # Unlock 3 batteries for the user
    user_battery = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_BATTERY)
    get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_BATTERY, new_amount=user_battery.item_quantity + 3)
    get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP, last_purchased_date=int(datetime.datetime.now().timestamp()))

    # Unlock an omnipotent bait for the user
    omnipotent_bait = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_OMNIPOTENT_BAIT)
    get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_OMNIPOTENT_BAIT, new_amount=omnipotent_bait.item_quantity + 1)
    get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_OMNIPOTENT_BAIT, last_purchased_date=int(datetime.datetime.now().timestamp()))

    return [
        ("Congratulations! You've unlocked the Basic Trap!! You can use this to capture creatures while AFK. Check the Trap Manager to view your current trap configurations.", convert_to_png(image=user_basic_trap.item_unlock_image, file_name="basic_trap_unlock.png")),
        ("Congratulations! You've unlocked three batteries for unlocking the Basic Trap!! You can use these to charge your trap. Check the Trap Manager to charge your trap.", convert_to_png(image=user_battery.item_unlock_image, file_name="battery_unlock.png")),
        ("Congratulations! You've unlocked an omnipotent bait to celebrate the one year anniversary of TGOMMO!! You can use this to summon any creature of your choice! Check your item inventory to use your bait!", convert_to_png(image=omnipotent_bait.item_unlock_image, file_name="omnipotentbait.png")),
    ]
# endregion
# endregion

# region Random Item Catch Rewards
async def check_for_random_item_catch_reward(user_id, interaction):
    notifications = await run_serialized_blocking(_prepare_random_item_catch_notification, user_id)
    for message, image in notifications:
        await interaction.followup.send(message, file=image, ephemeral=True)
    return bool(notifications)
def _prepare_random_item_catch_notification(user_id):
    notifications = []

    # BATTERY: 5% chance of a battery drop
    if random.randint(1, 20) == 1:
        battery_item = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_BATTERY)
        get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_BATTERY, new_amount=battery_item.item_quantity + 1)
        get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_BATTERY, last_purchased_date=int(datetime.datetime.now().timestamp()))

        notifications.append(("🎉 You found a battery while catching that creature!", convert_to_png(image=battery_item.item_unlock_image, file_name="battery_reward.png"),))

    # KINGDOM BAIT: 4% chance of a kingdom-specific bait drop
    if random.randint(1, 25) == 1:
        chosen_bait = resolve_static_content_cache(StaticItemCache).get_item_by_id(item_id=random.choice((ITEM_ID_MAMMAL_BAIT, ITEM_ID_BIRD_BAIT, ITEM_ID_REPTILE_BAIT)))

        bait_item = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=chosen_bait.item_id)
        get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=chosen_bait.item_id, new_amount=bait_item.item_quantity + 1)
        get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=chosen_bait.item_id, last_purchased_date=int(datetime.datetime.now().timestamp()))

        notifications.append((f"🎉 You found {chosen_bait.item_name} while catching that creature!", convert_to_png(image=bait_item.item_unlock_image, file_name="bait_reward.png"),))
    return notifications
# endregion

import datetime
import random

from src.commons.CommonFunctions import convert_to_png
from src.caching import resolve_static_content_cache
from src.caching.db_specific_caches.static_item_cache import StaticItemCache
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from resources.constants.TGO_MMO_constants import ITEM_ID_BASIC_TRAP, ITEM_ID_BATTERY, ITEM_ID_OMNIPOTENT_BAIT

# check if player has unlocked any items from catching creature
async def check_for_milestone_catch_rewards(user_id, interaction):
    # if user has not unlocked the basic trap, grant them this item
    user_catch_count = len(get_tgommo_db_handler().get_user_creatures_by_user_id(user_id=user_id))

    # check if user has unlocked the basic trap, if not, and they have caught 100 creatures, unlock the basic trap for them
    user_basic_trap = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP)
    if user_basic_trap.item_quantity == 0 and user_catch_count >= 100:
        # first load the player's trap link to ensure they have a trap link entry in the database
        get_tgommo_db_handler().get_player_trap_link_by_user_id(user_id=user_id)

        # next update the player's inventory to add the basic trap & when it was unlocked
        get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP, new_amount=1)
        get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP, last_purchased_date=int(datetime.datetime.now().timestamp()))

        # grant the user 3 batteries to start off with
        user_battery = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_BATTERY)
        get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_BATTERY, new_amount=user_battery.item_quantity + 3)
        get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_BASIC_TRAP, last_purchased_date=int(datetime.datetime.now().timestamp()))

        # todo - move this to the quest view once the quests are implemented. In the meantime, can use this as a base to reward omnipotent bait
        omnipotent_bait = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_OMNIPOTENT_BAIT)
        get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_OMNIPOTENT_BAIT, new_amount=omnipotent_bait.item_quantity + 1)
        get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_OMNIPOTENT_BAIT, last_purchased_date=int(datetime.datetime.now().timestamp()))

        # next, let the user know they have unlocked the basic trap and send them the image of the trap
        await interaction.followup.send(f"Congratulations! You've unlocked the Basic Trap!! You can use this to capture creatures while AFK. Check the Trap Manager to view your current trap configurations.", file=convert_to_png(image=user_basic_trap.item_unlock_image, file_name="basic_trap_unlock.png"), ephemeral=True)
        await interaction.followup.send(f"Congratulations! You've unlocked three batteries for unlocking the Basic Trap!! You can use these to charge your trap. Check the Trap Manager to charge your trap.", file=convert_to_png(image=user_battery.item_unlock_image, file_name="battery_unlock.png"), ephemeral=True)
        await interaction.followup.send(f"Congratulations! You've unlocked an omnipotent bait to celebrate the one year anniversary of TGOMMO!! You can use this to summon any creature of your choice! Check your item inventory to use your bait!", file=convert_to_png(image=omnipotent_bait.item_unlock_image, file_name="omnipotentbait.png"), ephemeral=True)

    return

# check if player should get a random battery reward from catching a creature
async def check_for_random_item_catch_reward(user_id, interaction):
    if random.randint(1, 20) != 1:
        return False

    #todo: we implemented grabbing items from the cache but need to implement player item caching; will use the database for now until we implement player item caching
    battery_item = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_BATTERY)
    # battery_item = resolve_static_content_cache(StaticItemCache).get_item_by_id(item_id=ITEM_ID_BATTERY)

    get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_BATTERY, new_amount=battery_item.item_quantity + 1,)
    get_tgommo_db_handler().update_user_avatar_item_last_purchased_date(user_id=user_id, item_id=ITEM_ID_BATTERY, last_purchased_date=int(datetime.datetime.now().timestamp()),)

    await interaction.followup.send("🎉 You found a battery while catching that creature!", file=convert_to_png(image=battery_item.item_unlock_image, file_name="battery_reward.png"), ephemeral=True,)
    return True

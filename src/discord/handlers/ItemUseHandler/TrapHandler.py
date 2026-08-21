# python
import random
import threading
from typing import Optional, Tuple, Dict

from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOCreature import TGOCreature
from src.resources.constants.TGO_MMO_constants import ITEM_ID_BASIC_TRAP, ITEM_ID_BATTERY, TRAP_ID_RARITY_MAP

# Global map storing user_id -> (battery_count, trap_id)
_TRAP_MAP_LOCK = threading.Lock()

class TrapHandler:
    # allows user to charge their trap using a battery, if they have one in their inventory
    @staticmethod
    def charge_trap(user_id: int, trap_id: Optional[int] = None, charge_count=8) -> int:
        with _TRAP_MAP_LOCK:
            battery_total = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=user_id, item_id=ITEM_ID_BATTERY).item_quantity
            if battery_total == 0:
                return battery_total
            if battery_total >= 0:
                user_trap_link = get_tgommo_db_handler().get_player_trap_link_by_user_id(user_id=user_id)
                get_tgommo_db_handler().update_user_trap_link_charges(user_id=user_id, player_trap_charges=min(user_trap_link.player_max_trap_charges, user_trap_link.player_trap_charges + charge_count))
                get_tgommo_db_handler().update_user_profile_available_items(user_id=user_id, item_id=ITEM_ID_BATTERY, new_amount=battery_total-1)
                return user_trap_link.player_trap_charges + charge_count

    @staticmethod
    def select_user_for_trap_capture(creature: TGOCreature):
        with _TRAP_MAP_LOCK:
            trap_battery_map: Dict[int, Tuple[int, int]] = {}

            player_trap_links = get_tgommo_db_handler().get_player_trap_links_for_server()
            for link in player_trap_links:
                trap_battery_map[link.player_id] = (link.player_trap_charges, link.active_trap.item_id)

            # first, filter out users with no battery chargers
            eligible_users = {uid: (count, trap_id) for uid, (count, trap_id) in trap_battery_map.items() if count > 0}

            # next, filter out users who have never caught a creature with this dex number
            users_who_have_caught_dex = get_tgommo_db_handler().get_users_who_caught_creature_by_dex_no(dex_no=creature.dex_no)
            eligible_users = {uid: (count, trap_id) for uid, (count, trap_id) in eligible_users.items() if uid in users_who_have_caught_dex}

            if len(eligible_users) == 0:
                return None

            # next, see if anyone has an active trap that coincides with the despawning creature's rarity
            users_with_matching_rarity = {uid: (count, trap_id) for uid, (count, trap_id) in eligible_users.items() if TRAP_ID_RARITY_MAP.get(trap_id) == creature.local_rarity.name}
            if users_with_matching_rarity:
                eligible_users = users_with_matching_rarity
            else:
                # if no one has a matching trap, we will filter to only pull from users who have a Basic Trap
                eligible_users = {uid: (count, trap_id) for uid, (count, trap_id) in eligible_users.items() if trap_id == ITEM_ID_BASIC_TRAP}

            if not eligible_users:
                return None

            # finally, let's grab a random user from the eligible users and decrement their battery count
            return random.choice(list(eligible_users.keys()))

    # swap trap associated with user's player trap link
    @staticmethod
    async def switch_trap(user_id: int, new_trap_id: int, interaction=None):
        with _TRAP_MAP_LOCK:
            try:
                get_tgommo_db_handler().update_user_trap_link_item_id(user_id=user_id, item_id=new_trap_id)
                if interaction:
                   await interaction.response.send_message(f"Successfully switched trap to {new_trap_id} for user {user_id}.", ephemeral=True)
                return True
            except Exception as e:
                print(f"Error switching trap for user {user_id}: {e}")
                return False
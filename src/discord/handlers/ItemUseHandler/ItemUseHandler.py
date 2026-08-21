import time
import asyncio
from typing import List, Tuple

from src.commons.CommonFunctions import *
from src.commons.GameStateManager import get_game_state_manager
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.handlers.ItemUseHandler.NametagUseView import NametagUseView
from src.discord.handlers.ItemUseHandler.TrapHandler import TrapHandler
from src.discord.objects.TGOPlayer import TGOPlayer
from src.discord.objects.TGOPlayerItem import TGOPlayerItem
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class ItemUseHandler:
    def __init__(self, channel, discord_bot, original_view=None, original_message=None):
        self.discord_bot = discord_bot
        self.channel = channel

        self.original_view = original_view
        self.original_message = original_message

        self.active_effect = {
            ITEM_TYPE_NAMETAG: self.use_nametag,
            ITEM_TYPE_CHARM: self.use_creature_charm,
            ITEM_TYPE_BAIT: self.use_bait,
            ITEM_TYPE_BATTERY: self.use_battery,
            ITEM_TYPE_TRAP: self.use_trap
        }


    async def use_item(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        # capture the channel where the interaction occurred so background tasks can send messages later
        self.channel = interaction.channel

        # check to make sure user has at least 1 in their inventory before allowing use
        if get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(item_id=item.item_id, user_id=user.user_id, convert_to_object=True).item_quantity > 0 and item.item_type in self.active_effect:
            affect_activated, response_message = await self.active_effect[item.item_type](user=user, item=item, interaction=interaction)

            # remove an item from the user after the effect is applied
            if affect_activated:
                # remove the item from the user's inventory assuming its not a key item
                if item.item_type not in UNLIMITED_INVENTORY_ITEM_TYPES:
                    get_tgommo_db_handler().update_user_profile_available_items(user_id=user.user_id, item_id=item.item_id, new_amount=get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(item_id=item.item_id, user_id=user.user_id, convert_to_object=True).item_quantity - 1)
                if response_message:
                    await interaction.channel.send(response_message, files=[convert_to_png(item.item_image, "item_img.png")])

                await self.original_message.edit(attachments=[self.original_view.reload_image(target_user=user)], view=self.original_view)

            elif response_message:
                await interaction.followup.send(response_message, ephemeral=True)
        else:
            await interaction.followup.send(f"You don't got any {item.item_name}s left to use, dude...", ephemeral=True)


    '''---- ITEM EFFECT HANDLERS ------------------------------------------------------------------------------------------------------------'''

    async def use_nametag(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        nametag_view = NametagUseView(target_user=user, item_use_handler=self)
        await interaction.followup.send(f"You used the {item.item_name}! You can now rename your creature.", view=nametag_view, ephemeral=True)
        return False, None

    async def use_plane_ticket(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        # todo: logic for wildcard plane ticket for user to select their environment

        # logic to determine the kingdom and rarity of the creature to spawn based on the plane ticket item used
        new_environment_dex_no = item_id_plane_ticket_map.get(item.item_id)
        new_environment = get_tgommo_db_handler().get_environments_by_dex_no(dex_no=new_environment_dex_no, convert_to_object=True)

        # todo: add a function to creature_spawner_handler to gracefully change the environment and handle any necessary cleanup or state updates
        self.discord_bot.creature_spawner_handler.current_environment = new_environment

        return True, f"<@{user.user_id}> *({user.nickname})* used the {item.item_name}!"

    '''---- CREATURE SPAWN BONUS HANDLERS ------------------------------------------------------------------------------------------------------------'''
    # Applies the effect of a bait item. Before applying the effect, it checks if the server has captured at least 65% of the unique creatures in the current environment. If not, it returns False and a message indicating that bait use is locked until 65% capture is reached. If the capture requirement is met, it spawns a creature with the appropriate rarity and returns True along with a message indicating that the bait was used.
    async def use_bait(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        # omnipotent bait bypasses the 65% capture requirement and allows the user to spawn a creature of their choice
        if item.item_id == ITEM_ID_OMNIPOTENT_BAIT:
            return await self.use_omnipotent_bait(user=user, item=item, interaction=interaction)

        # check if server has captured at least 65% of creatures in the current environment before allowing bait use
        available_unique_creatures_for_environment = get_tgommo_db_handler().get_total_unique_creatures_available_for_environment(environment_dex_no=self.discord_bot.creature_spawner_handler.current_environment.dex_no, include_variants=True)
        caught_unique_creatures_for_environment = get_tgommo_db_handler().get_total_unique_creature_variants_caught_in_environment(environment_dex_no=self.discord_bot.creature_spawner_handler.current_environment.dex_no)
        capture_percentage = (caught_unique_creatures_for_environment / available_unique_creatures_for_environment) * 100

        if capture_percentage < 65:
            return False, f"You can't use bait yet! Only {capture_percentage:.1f}% of creatures in {self.discord_bot.creature_spawner_handler.current_environment.name} have been captured by the server. Baits unlock at 65%."

        # logic to determine the kingdom and rarity of the creature to spawn based on the bait item used
        kingdom = kingdom_bait_map.get(item.item_id)
        rarity = rarity_bait_map.get(item.item_id)

        await self.discord_bot.creature_spawner_handler.spawn_creature(user=user, rarity=rarity, kingdom=kingdom)
        return True, f"<@{user.user_id}> *({user.nickname})* used the {item.item_name}!"

    # Applies the effect of the omnipotent bait item. This item bypasses the 65% capture requirement and allows the user to spawn a creature of their choice. The function calls the creature spawner handler to spawn a creature without specifying rarity or kingdom, allowing for user selection.
    async def use_omnipotent_bait(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        # todo: pull up menu for selecting a specific creature to spawn
        await self.discord_bot.creature_spawner_handler.spawn_creature(user=user, rarity=None, kingdom=None)
        return True, f"<@{user.user_id}> *({user.nickname})* used the {item.item_name}!"

    # Applies the effect of a charm item. If a charm of the same type is already active, it returns False and a message indicating that the charm is already active. Otherwise, it adds the charm effect to the game state manager and schedules its removal after 15 minutes.
    async def use_creature_charm(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        charm_groups = [
            (set(CHARM_IDS), f"A Charm is already active! Please wait for it to wear off before using another Charm."),
            (set(MYTHICAL_CHARM_IDS), f"A Mythical Charm is already active! Please wait for it to wear off before using another Mythical Charm."),
            (set(RARITY_CHARM_MAP.keys()), f"A Rarity Charm is already active! Please wait for it to wear off before using another Rarity Charm."),
            (set(KINGDOM_CHARM_MAP.keys()), f"A Kingdom Charm is already active! Please wait for it to wear off before using another Kingdom Charm."),
        ]
        successful, msg = await self._use_timed_item(user=user, item=item, interaction=interaction, groups=charm_groups, failure_msg="A charm with this effect is already active! Please wait for it to wear off before using another charm.", item_type=ITEM_TYPE_CHARM, duration_minutes=15)

        # todo: this is not working correctly
        # spawn a bonus creature if the charm was successfully activated
        await self.discord_bot.creature_spawner_handler.spawn_creature(user=user, rarity=None, kingdom=None)

        return successful, msg

    #todo: use amulet coin
    #todo: use time charm


    '''---- CREATURE TRAP HANDLERS ------------------------------------------------------------------------------------------------------------'''
    async def use_battery(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        new_charges = TrapHandler.charge_trap(user_id=user.user_id)
        await interaction.followup.send(f"You've successfully charged your Trap! You now have {new_charges} charges remaining.", ephemeral=True)
        return True, None

    async def use_trap(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        await TrapHandler.switch_trap(user_id=user.user_id, new_trap_id=item.item_id, interaction=interaction)
        await interaction.followup.send(f"You've successfully switched your Trap! {item.item_name} is now active.", ephemeral=True)
        return True, None


    '''---- TIMED ITEM ACTIONS ------------------------------------------------------------------------------------------------------------'''
    # Generalized function for using timed items like charms. It checks if an item from the same group is already active, and if not, it adds the new item effect to the game state manager and schedules its removal after a specified duration. The groups parameter is a list of tuples, where each tuple contains a set of item IDs that belong to the same group and a message to display if an item from that group is already active.
    async def _use_timed_item(self, user: TGOPlayer, item: TGOPlayerItem, interaction, groups: List[Tuple[set, str]], failure_msg: str, item_type=ITEM_TYPE_CHARM, duration_minutes: int = 15):
        active_bonuses = get_game_state_manager().get_active_spawn_bonuses()

        # check if a same-group item is already active
        for group_ids, msg in groups:
            if item.item_id in group_ids and any(active_item.item_id in group_ids for active_item in active_bonuses):
                return False, msg

        # add the timed effect
        despawn_timestamp = int(time.time()) + (duration_minutes * 60)
        bonus_added = get_game_state_manager().add_active_spawn_bonus(item_id=item.item_id, despawn_ts=despawn_timestamp)
        if not bonus_added:
            return False, failure_msg

        # schedule removal (background) — do NOT await create_task
        asyncio.create_task(self._schedule_effect_removal(despawn_ts=despawn_timestamp, item=item))
        return True, f"<@{user.user_id}> *({user.nickname})* used the {item.item_name}. Effects are active for the next {duration_minutes} minutes!"

    # Schedules the removal of an active item effect after a specified delay. It calculates the delay based on the current time and the provided despawn timestamp, then sleeps for that duration before removing the effect from the game state manager and sending a message to the channel indicating that the effect has worn off.
    async def _schedule_effect_removal(self, despawn_ts: int, item):
        # compute remaining delay and sleep inside this coroutine
        delay = max(0, despawn_ts - int(time.time()))
        await asyncio.sleep(delay)

        # remove the effect and notify channel
        get_game_state_manager().remove_active_spawn_bonus(item_id=item.item_id)

        # Attempt to send a notification to the stored channel. If none is available, skip sending but
        try:
            await self.channel.send(f"The effect of {item.item_name} has worn off.", files=[to_grayscale(self.get_image_for_item(item))])
        except Exception as e:
            print(f"ItemUseHandler: failed to send expiration message for {item.item_name}: {e}")


    '''---- SUPPORT FUNCTIONS ------------------------------------------------------------------------------------------------------------'''
    def get_image_for_item(self, item: TGOPlayerItem):
        return convert_to_png(Image.open(f"{ITEM_BASE}{item.img_root}{IMAGE_FILE_EXTENSION}"), f'item_img.png')
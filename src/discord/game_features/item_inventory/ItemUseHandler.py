import threading
import time

from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.objects.TGOPlayer import TGOPlayer
from src.discord.objects.TGOPlayerItem import TGOPlayerItem
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *


class ItemUseHandler:
    def __init__(self, channel, discord_bot):
        self.discord_bot = discord_bot
        self.channel = channel

        self.active_effect = {
            ITEM_TYPE_NAMETAG: self.use_nametag,
            ITEM_TYPE_CHARM: self.use_charm,
            ITEM_TYPE_BAIT: self.use_bait,
        }


    async def use_item(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        # check to make sure user has at least 1 bait
        if get_tgommo_db_handler().get_user_item_by_user_id_and_item_id(item_id=item.item_id, user_id=user.user_id, convert_to_object=True).item_quantity > 0 and item.item_type in self.active_effect:
            affect_successful, response_message = await self.active_effect[item.item_type](user=user, item=item, interaction=interaction)

            # remove an item from the user after the effect is applied
            if affect_successful:
                get_tgommo_db_handler().update_user_profile_available_items(user_id=user.user_id, item_id=item.item_id, new_amount=get_tgommo_db_handler().get_user_item_by_user_id_and_item_id(item_id=item.item_id, user_id=user.user_id, convert_to_object=True).item_quantity - 1)
                if response_message:
                    await interaction.channel.send(response_message, files=[self.get_image_for_item(item)])
            elif response_message:
                await interaction.followup.send(response_message, ephemeral=True)
        else:
            await interaction.followup.send(f"You don't got any {item.item_name}s left to use, dude...", ephemeral=True)


    '''############ ITEM EFFECT HANDLERS ############'''
    async def use_nametag(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        # todo: open module to rename creature
        await interaction.followup.send(f"You used the nametag! You can now rename your creature.", ephemeral=True)
        await self.channel.send(f"<@{user.user_id}> ({user.nickname}) used nametag! You can now rename your creature.")
        return True


    async def use_charm(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        bonus_type = ITEM_TYPE_CHARM
        if item.item_id == ITEM_ID_CHARM:
            bonus_type += TGOMMO_RARITY_NORMAL
        elif item.item_id == ITEM_ID_MYTHICAL_CHARM:
            bonus_type += TGOMMO_RARITY_MYTHICAL

        # add spawn bonus to creature spawner
        bonus_added = self.discord_bot.creature_spawner_handler.add_spawn_bonus(bonus_type=bonus_type, bonus_name=item.item_name, rarity=item.rarity.name, image=self.get_image_for_item(item))

        if not bonus_added:
            return False, f"A charm with this effect is already active! Please wait for it to wear off before using another charm."

        # schedule effect removal
        await asyncio.create_task(self._schedule_charm_effect_removal(duration_seconds=15 * 60, item=item, bonus_type = bonus_type))
        return True, f"<@{user.user_id}> *({user.nickname})* used the {item.item_name}. Effects are active for the next 15 minutes!"



    async def use_bait(self, user: TGOPlayer, item: TGOPlayerItem, interaction):
        # check if server has captured at least 65% of creatures in the current environment before allowing bait use
        total_creatures = len(get_tgommo_db_handler().get_creatures_for_environment_by_dex_no(dex_no=self.discord_bot.creature_spawner_handler.current_environment.dex_no))
        captured_creatures = get_tgommo_db_handler().get_user_catch_totals_for_environment(include_variants=True, include_mythics=False, environment=self.discord_bot.creature_spawner_handler.current_environment, time_of_day=BOTH)[1]
        capture_percentage = (captured_creatures / total_creatures) * 100 if total_creatures > 0 else 0

        if capture_percentage < 65:
            return False, f"You can't use bait yet! Only {capture_percentage:.1f}% of creatures in {self.discord_bot.creature_spawner_handler.current_environment.name} have been captured by the server. Baits unlock at 65%."

        await self.discord_bot.creature_spawner_handler.spawn_creature(user=user, rarity=item.rarity if item.rarity.name != TGOMMO_RARITY_NORMAL else None)
        return True, f"<@{user.user_id}> *({user.nickname})* used the {item.item_name}!"


    '''############ AFFECT ACTIONS ############'''
    async def _schedule_charm_effect_removal(self, duration_seconds: int, item, bonus_type):
        thread = threading.Thread(target=self._execute_charm_removal, args=(duration_seconds, item, bonus_type))
        thread.daemon = True
        thread.start()

    def _execute_charm_removal(self, duration_seconds: int, item, bonus_type):
        time.sleep(duration_seconds)
        self.discord_bot.creature_spawner_handler.remove_spawn_bonus(bonus_type=bonus_type)
        # await self.channel.send(f"The effect of {item.item_name} has worn off.", files=[self.get_image_for_item(item)])


    '''############ SUPPORT FUNCTIONS ############'''
    def get_image_for_item(self, item: TGOPlayerItem):
        return convert_to_png(Image.open(f"{ITEM_INVENTORY_ITEM_BASE}{item.img_root}{IMAGE_FILE_EXTENSION}"), f'item_img.png')
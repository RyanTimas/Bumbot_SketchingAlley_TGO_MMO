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
            await self.active_effect[item.item_type](user=user, item=item)

            # remove an item from the user after the effect is applied
            get_tgommo_db_handler().update_user_profile_available_items(user_id=user.user_id, item_id=item.item_id, new_amount=get_tgommo_db_handler().get_user_item_by_user_id_and_item_id(item_id=item.item_id, user_id=user.user_id, convert_to_object=True).item_quantity - 1)
        else:
            await interaction.followup.send(f"You don't got any {item.item_name}s left to use, dude...", ephemeral=True)


    '''############ ITEM EFFECT HANDLERS ############'''
    async def use_nametag(self, user: TGOPlayer, item: TGOPlayerItem):
        # todo: open module to rename creature
        await self.channel.send(f"{user.nickname} used nametag! You can now rename your creature.")


    async def use_charm(self, user: TGOPlayer, item: TGOPlayerItem):
        # todo: implement charm effect
        await self.handle_channel_communication(user, item)


    async def use_bait(self, user: TGOPlayer, item: TGOPlayerItem):
        await self.discord_bot.creature_spawner_handler.spawn_creature(user=user, rarity=item.rarity if item.rarity.name != TGOMMO_RARITY_NORMAL else None)

    '''############ SUPPORT FUNCTIONS ############'''
    async def handle_channel_communication(self, user: TGOPlayer, item: TGOPlayerItem):
        item_img = convert_to_png(Image.open(f"{ITEM_INVENTORY_ITEM_BASE}{item.img_root}{IMAGE_FILE_EXTENSION}"), f'item_img.png')

        await self.channel.send(content=f"{user.nickname} has used {item.item_name}. Effects are active for the next 15 minutes!", files=[item_img])
        # Schedule effect removal
        await asyncio.create_task(self._schedule_effect_removal(duration_seconds=15 * 60, item_name=item.item_name, item_img = item_img))


    async def _schedule_effect_removal(self, duration_seconds: int, item_name: str, item_img):
        """Schedule the removal of a temporary effect"""
        await asyncio.sleep(duration_seconds)
        await self.channel.send(f"The effect of {item_name} has worn off.", files=[item_img])
import os

from PIL import Image
from src.discord.handlers.ItemUnlockHandler.ItemUnlockImageFactory import ItemUnlockImageFactory
from src.discord.objects.CreatureRarity import CreatureRarity
from src.resources.constants.file_paths import ITEM_BASE, IMAGE_FILE_EXTENSION


class TGOPlayerItem:
    def __init__(self,
        item_num:int, item_id: int,
        item_name: str, item_type: str, item_category: str, item_description: str,
        rarity:CreatureRarity, is_rewardable: bool, img_root: str, default_uses: int =0,
        user_id: int =0, item_quantity: int =0, last_used: int =0,
        last_purchase_date: int =0, shop_price: int =0,
        despawn_timestamp: int =0
    ):
        self.item_num = item_num
        self.item_id = item_id

        self.item_name = item_name
        self.item_type = item_type
        self.item_category = item_category
        self.item_description = item_description

        self.rarity = rarity
        self.is_rewardable = is_rewardable
        self.img_root = img_root if img_root != '' else f"{item_type.lower()}_{rarity.name.lower()}"
        self.default_uses = default_uses

        self.user_id = user_id if user_id else -1
        self.item_quantity = item_quantity
        self.last_used = last_used if last_used else -1

        self.shop_price = shop_price
        self.last_purchase_date = last_purchase_date if last_purchase_date else -1

        # IMAGES
        self.item_image = None
        self.item_unlock_image = None
        self.define_item_image()
        self.despawn_timestamp = despawn_timestamp if despawn_timestamp else None

    def define_item_image(self):
        item_img_path = f"{ITEM_BASE}{self.img_root}{IMAGE_FILE_EXTENSION}"
        fallback_img_root_path = f"{ITEM_BASE}Fallback{IMAGE_FILE_EXTENSION}"

        with Image.open(item_img_path if os.path.exists(item_img_path) else fallback_img_root_path) as img:
            self.item_image = img.copy()

        self.item_unlock_image = ItemUnlockImageFactory(item=self).generate_item_unlock_image()
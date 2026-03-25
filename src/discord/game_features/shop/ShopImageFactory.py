from src.commons.CommonFunctions import *
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.player_profile.PlayerProfileSidePanelTabFactory import PlayerProfileSidePanelTabFactory
from src.discord.game_features.shop.ShopItemImageFactory import ShopItemImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *

class ShopImageFactory(BaseImageFactory):
    def __init__(self, message_author):
        super().__init__(message_author=message_author, target_user=message_author)
        self.load_relevant_info()

    def build_image(self):
        shop_image = Image.open(SHOP_BG_IMAGE)
        corner_overlay_image = Image.open(SHOP_CORNER_OVERLAY_IMAGE)
        morshu_overlay_image = Image.open(SHOP_MORSHU_OVERLAY_IMAGE)
        top_shelf_image = Image.open(SHOP_TOP_SHELF_IMAGE)
        bottom_shelf_image = Image.open(SHOP_BOTTOM_SHELF_IMAGE)

        shop_image.paste(top_shelf_image, (0, 0), top_shelf_image)
        shop_image.paste(bottom_shelf_image, (0, 0), bottom_shelf_image)

        self.load_daily_shop_inventory(shop_image=shop_image)

        shop_image.paste(morshu_overlay_image, (0, 0), morshu_overlay_image)
        shop_image.paste(corner_overlay_image, (0, 0), corner_overlay_image)

        return shop_image

    def load_daily_shop_inventory(self, shop_image):
        # todo: get random items and avatars from database instead of hardcoding
        test_item_image_1 = ShopItemImageFactory(item=get_tgommo_db_handler().get_inventory_item_by_item_id("NameTag_1")).generate_shop_item_image().resize((280, 280), Image.LANCZOS)
        test_item_image_2 = ShopItemImageFactory(item=get_tgommo_db_handler().get_inventory_item_by_item_id("Charm_7")).generate_shop_item_image().resize((280, 280), Image.LANCZOS)
        test_item_image_3 = ShopItemImageFactory(item=get_tgommo_db_handler().get_inventory_item_by_item_id("Bait_8")).generate_shop_item_image().resize((280, 280), Image.LANCZOS)

        test_avatar_image_1 = ShopItemImageFactory(avatar=get_tgommo_db_handler().get_avatar_by_id("S6")).generate_shop_item_image().resize((280, 280), Image.LANCZOS)
        test_avatar_image_2 = ShopItemImageFactory(avatar=get_tgommo_db_handler().get_avatar_by_id("S4")).generate_shop_item_image().resize((280, 280), Image.LANCZOS)
        test_avatar_image_3 = ShopItemImageFactory(avatar=get_tgommo_db_handler().get_avatar_by_id("S2")).generate_shop_item_image().resize((280, 280), Image.LANCZOS)


        # place daily items on top shelf
        shop_image.paste(test_item_image_1, (844, 137), test_item_image_1)
        shop_image.paste(test_item_image_2, (1160, 120), test_item_image_2)
        shop_image.paste(test_item_image_3, (1460, 120), test_item_image_3)

        # place daily avatars on bottom shelf
        shop_image.paste(test_avatar_image_1, (960, 536), test_avatar_image_1)
        shop_image.paste(test_avatar_image_2, (1300, 536), test_avatar_image_2)
        shop_image.paste(test_avatar_image_3, (1648, 536), test_avatar_image_3)



from src.commons.CommonFunctions import *
from src.commons.GameStateManager import game_state_manager, get_game_state_manager
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.player_profile.PlayerProfileSidePanelTabFactory import PlayerProfileSidePanelTabFactory
from src.discord.game_features.shop.ShopItemImageFactory import ShopItemImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *

class ShopImageFactory(BaseImageFactory):
    def __init__(self, message_author, shop_items=[], shop_avatars=[]):
        super().__init__(message_author=message_author, target_user=message_author)
        self.shop_items = shop_items
        self.shop_avatars = shop_avatars

        # todo: move out of class
        self.shop_items, self.shop_avatars = get_game_state_manager().get_current_shop_inventory()

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

        # todo: add player currency overlay

        return shop_image

    def load_daily_shop_inventory(self, shop_image):
        for i, item in enumerate(self.shop_items):
            item_image_factory = ShopItemImageFactory(item=item)
            item_image = item_image_factory.generate_shop_item_image().resize((280, 280), Image.LANCZOS)
            shop_image.paste(item_image, (860 + 300*i, 120), item_image)

        for i, avatar in enumerate(self.shop_avatars):
            avatar_image_factory = ShopItemImageFactory(avatar=avatar)
            avatar_image = avatar_image_factory.generate_shop_item_image().resize((280, 280), Image.LANCZOS)
            shop_image.paste(avatar_image, (960 + 340*i, 536), avatar_image)



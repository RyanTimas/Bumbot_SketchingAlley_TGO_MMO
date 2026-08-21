from src.commons.CommonFunctions import *
from src.commons.GameStateManager import game_state_manager, get_game_state_manager
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.player_profile.PlayerProfileSidePanelTabFactory import PlayerProfileSidePanelTabFactory
from src.discord.game_features.shop.ShopItemImageFactory import ShopItemImageFactory
from src.discord.general.template.BaseImageFactory import BaseImageFactory
from src.resources.constants.TGO_MMO_constants import *
from src.resources.constants.file_paths import *

class ShopImageFactory(BaseImageFactory):
    def __init__(self, message_author):
        super().__init__(message_author=message_author, target_user=message_author)

        self.shop_items, self.shop_avatars = get_game_state_manager().get_current_shop_inventory()

        self.load_relevant_info()

    def build_image(self):
        # build base shop image
        shop_image = Image.open(SHOP_BG_IMAGE)
        currency_overlay_image = Image.open(SHOP_CURRENCY_OVERLAY_IMAGE)
        top_shelf_image = Image.open(SHOP_TOP_SHELF_IMAGE)
        bottom_shelf_image = Image.open(SHOP_BOTTOM_SHELF_IMAGE)

        # build shelves and place inventory on image
        shop_image.paste(top_shelf_image, (0, 0), top_shelf_image)
        shop_image.paste(bottom_shelf_image, (0, 0), bottom_shelf_image)
        self.place_shop_inventory_on_image(shop_image=shop_image)

        # build morshu section
        morshu_overlay_image = Image.open(SHOP_MORSHU_OVERLAY_IMAGE)
        shop_image.paste(morshu_overlay_image, (0, 0), morshu_overlay_image)
        if get_game_state_manager().get_shop_level() == 2:
            battery_overlay_image = Image.open(SHOP_BATTERY_BASKET_IMAGE)
            shop_image.paste(battery_overlay_image, (0, 0), battery_overlay_image)
        if get_game_state_manager().get_shop_upgrade_in_progress():
            upgrade_overlay_image = Image.open(SHOP_UPGRADE_SIGN_IMAGE)
            shop_image.paste(upgrade_overlay_image, (0, 0), upgrade_overlay_image)

        # add currency overlay to image
        shop_image.paste(currency_overlay_image, (0, 0), currency_overlay_image)
        self.add_text_to_image(shop_image)

        # add corner overlay to image
        corner_overlay_image = Image.open(SHOP_CORNER_OVERLAY_IMAGE)
        shop_image.paste(corner_overlay_image, (0, 0), corner_overlay_image)

        return shop_image

    def place_shop_inventory_on_image(self, shop_image):
        for i, item in enumerate(self.shop_items):
            item_image_factory = ShopItemImageFactory(item=item)

            user_bought_item_today = get_tgommo_db_handler().get_inventory_item_by_user_id_and_item_id(user_id=self.message_author.user_id, item_id=item.item_id).last_purchase_date == get_game_state_manager().get_shop_date()
            item_image = item_image_factory.generate_shop_item_image(is_sold_out=user_bought_item_today).resize((280, 280), Image.LANCZOS)
            shop_image.paste(item_image, (860 + 300*i, 120), item_image)

        for i, avatar in enumerate(self.shop_avatars):
            avatar_image_factory = ShopItemImageFactory(avatar=avatar)

            user_owns_avatar = get_tgommo_db_handler().has_user_unlocked_avatar(user_id=self.message_author.user_id, avatar_id=avatar.avatar_id)
            avatar_image = avatar_image_factory.generate_shop_item_image(is_sold_out=user_owns_avatar).resize((280, 280), Image.LANCZOS)
            shop_image.paste(avatar_image, (960 + 340*i, 536), avatar_image)

    def add_text_to_image(self, image: Image):
        draw = ImageDraw.Draw(image)

        # ADD PLAYER'S CURRENCY BALANCE TO IMAGE
        font = resize_text_to_fit(text=f"{self.message_author.currency}", draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 65), max_width=276, min_font_size=7)
        draw.text(get_centered_text_position(text=f"{self.message_author.currency}", font=font, center_pixel_location=(1686, 62)), f"{self.message_author.currency}", fill=FONT_COLOR_BLACK, font=font)

        # ADD CURRENT DONATION & DONATION GOAL TO IMAGE
        if get_game_state_manager().get_shop_upgrade_in_progress():
            donation_amount = f"{get_game_state_manager().get_shop_donation_total()}"
            donation_goal = f"{SHOP_LEVEL_COST_MAP[get_game_state_manager().get_shop_level()]}"

            donation_font = resize_text_to_fit(text=donation_goal, draw=draw, font=ImageFont.truetype(FONT_FOREST_REGULAR_FILE, 40), max_width=120, min_font_size=7)

            draw.text(get_centered_text_position(text=donation_amount, font=donation_font, center_pixel_location=(272, 972)), donation_amount, fill=FONT_COLOR_WHITE, font=donation_font)
            draw.text(get_centered_text_position(text=donation_goal, font=donation_font, center_pixel_location=(672, 972)), donation_goal, fill=FONT_COLOR_WHITE, font=donation_font)
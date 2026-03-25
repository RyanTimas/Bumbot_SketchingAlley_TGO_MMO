from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarBoardImageFactory import AvatarBoardImageFactory
from src.discord.game_features.avatar_board.AvatarBoardView import AvatarBoardView
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.creature_inventory.CreatureInventoryView import CreatureInventoryView
from src.discord.game_features.encyclopedia_location_index.EncyclopediaLocationIndexImageFactory import \
    EncyclopediaLocationIndexImageFactory
from src.discord.game_features.encyclopedia_location_index.EncyclopediaLocationIndexView import \
    EncyclopediaLocationIndexView
from src.discord.game_features.item_inventory.ItemInventoryImageFactory import ItemInventoryImageFactory
from src.discord.game_features.item_inventory.ItemInventoryView import ItemInventoryView
from src.discord.game_features.player_profile.PlayerProfileImageFactory import PlayerProfileImageFactory
from src.discord.game_features.player_profile.PlayerProfileView import PlayerProfileView
from src.discord.game_features.shop.ShopImageFactory import ShopImageFactory


# ... other imports for views

def register_shop_tests(bot):
    @bot.command(name="TEST--generate_shop_image")
    async def generate_shop_image_test(ctx):
        user_id = ctx.author.id
        message_author = get_tgommo_db_handler().get_user_profile_by_user_id(user_id)

        try:
            # Create ShopImageFactory instance
            shop_factory = ShopImageFactory(message_author)

            # Generate the shop image
            shop_image_result = shop_factory.reload_image()

            # Send the image to Discord
            await ctx.send("Shop image generated successfully!", file=convert_to_png(shop_image_result, "test_img.png"))

        except Exception as e:
            await ctx.send(f"Error generating shop image: {str(e)}")
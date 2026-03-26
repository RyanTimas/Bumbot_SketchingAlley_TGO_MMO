import traceback

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.shop.ShopImageFactory import ShopImageFactory
from src.discord.game_features.shop.ShopView import ShopView


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

    @bot.command(name="TEST--shop_view")
    async def shop_view_test(ctx):
        user_id = ctx.author.id
        message_author = get_tgommo_db_handler().get_user_profile_by_user_id(user_id)

        try:
            shop_factory = ShopImageFactory(message_author)
            shop_view = ShopView(message_author, shop_factory)

            shop_image = shop_factory.reload_image()

            # Send the image with the view
            await ctx.send(
                "Shop view test - interact with the buttons below:",
                file=convert_to_png(shop_image, "shop_view_test.png"),
                view=shop_view
            )

        except Exception as e:
            print(f"Error in shop_view_test: {str(e)}")
            traceback.print_exc()

            await ctx.send(f"Error creating shop view: {str(e)}")
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord.game_features.avatar_board.AvatarBoardImageFactory import AvatarBoardImageFactory
from src.discord.game_features.avatar_board.AvatarBoardView import AvatarBoardView
from src.discord.game_features.creature_inventory.CreatureInventoryImageFactory import CreatureInventoryImageFactory
from src.discord.game_features.creature_inventory.CreatureInventoryView import CreatureInventoryView
from src.discord.game_features.encyclopedia.encyclopedia_location_index.EncyclopediaLocationIndexImageFactory import EncyclopediaLocationIndexImageFactory
from src.discord.game_features.encyclopedia.encyclopedia_location_index.EncyclopediaLocationIndexView import EncyclopediaLocationIndexView
from src.discord.game_features.item_inventory.ItemInventoryImageFactory import ItemInventoryImageFactory
from src.discord.game_features.item_inventory.ItemInventoryView import ItemInventoryView
from src.discord.game_features.player_profile.PlayerProfileImageFactory import PlayerProfileImageFactory
from src.discord.game_features.player_profile.PlayerProfileView import PlayerProfileView

def register_general_tests(bot):
    @bot.command(name="TEST--generate_all_views")
    async def generate_all_views(ctx):
        """Spawns all TGOMMO views at once for testing"""
        user_id = ctx.author.id
        message_author = get_tgommo_db_handler().get_user_profile_by_user_id(user_id)
        target_user = message_author

        await ctx.send(f"{ctx.author.mention} Spawning all TGOMMO views...")

        try:
            from src.discord.game_features.TGOMMOMenuView import TGOMMOMenuView
            view1 = TGOMMOMenuView(message_author=message_author, target_user=target_user, discord_bot=bot)
            await ctx.send('**TGOMMO Menu**', view=view1)

            avatar_board_factory = AvatarBoardImageFactory(message_author=message_author, target_user=target_user)
            view2 = AvatarBoardView(message_author=message_author, target_user=target_user, avatar_board_image_factory=avatar_board_factory)
            await ctx.send('**Avatar Board**', files=[view2.reload_image()], view=view2)

            creature_inventory_factory = CreatureInventoryImageFactory(message_author=message_author, target_user=target_user)
            view3 = CreatureInventoryView(message_author=message_author, target_user=target_user, creature_inventory_image_factory=creature_inventory_factory)
            await ctx.send('**Creature Inventory**', files=[view3.reload_image()], view=view3)

            encyclopedia_factory = EncyclopediaLocationIndexImageFactory(message_author=message_author, target_user=target_user)
            view4 = EncyclopediaLocationIndexView(message_author=message_author, target_user=target_user, encyclopedia_location_index_image_factory=encyclopedia_factory)
            await ctx.send('**Encyclopedia**', files=[view4.reload_image()], view=view4)

            item_inventory_factory = ItemInventoryImageFactory(message_author=message_author, target_user=target_user)
            view5 = ItemInventoryView(message_author=message_author, target_user=target_user, item_inventory_image_factory=item_inventory_factory, discord_bot=bot)
            await ctx.send('**Item Inventory**', files=[view5.reload_image()], view=view5)

            player_profile_factory = PlayerProfileImageFactory(message_author=message_author, target_user=target_user)
            view6 = PlayerProfileView(message_author=message_author, target_user=target_user, player_profile_image_factory=player_profile_factory)
            await ctx.send('**Player Profile**', files=[view6.reload_image()], view=view6)

        except Exception as e:
            await ctx.send(f"Error spawning views: {str(e)}")
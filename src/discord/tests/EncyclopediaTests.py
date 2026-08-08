from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.commons.CommonFunctions import convert_to_png
from src.discord.game_features.encyclopedia.EncyclopediaImageFactory import EncyclopediaImageFactory


def register_encyclopedia_tests(bot):
    @bot.command(name="TEST--generate_encyclopedia_pages")
    async def generate_encyclopedia_pages(ctx, environment_id: int = None):
        """Generate encyclopedia page images for an environment (or all environments if not provided)."""
        try:
            user_id = ctx.author.id
            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(user_id)

            if environment_id:
                env = get_tgommo_db_handler().get_environment_by_id(environment_id)
                envs = [env] if env else []
            else:
                envs = get_tgommo_db_handler().get_all_environments_in_rotation()

            total = len(envs)
            await ctx.send(f"Starting encyclopedia generation for {total} environment(s)...")

            for i, env in enumerate(envs, start=1):
                try:
                    # Create encyclopedia page factory for this environment and generate the page image
                    factory = EncyclopediaImageFactory(environment=env, message_author=message_author, target_user=message_author)
                    image = factory.reload_image()
                    await ctx.send(f"Generated encyclopedia for: {env.name} ({i}/{total})", file=convert_to_png(image, f"encyclopedia_{env.dex_no}.png"))
                except Exception as e:
                    await ctx.send(f"Failed generating for {env.name if env else environment_id}: {e}")
        except Exception as e:
            await ctx.send(f"Error in test: {e}")

    @bot.command(name="TEST--open_encyclopedia_view")
    async def open_encyclopedia_view(ctx, user_id: str = None):
        """Open the encyclopedia view for a user (uses same view as the app)."""
        try:
            target_user_id = int(user_id) if user_id and user_id.isdigit() else ctx.author.id
            message_author = get_tgommo_db_handler().get_user_profile_by_user_id(ctx.author.id)
            target_user = get_tgommo_db_handler().get_user_profile_by_user_id(target_user_id)

            # Determine a default environment (first in rotation) for the encyclopedia page view
            envs = get_tgommo_db_handler().get_all_environments_in_rotation()
            env = envs[0] if envs else get_tgommo_db_handler().get_environment_by_id(1)
            factory = EncyclopediaImageFactory(environment=env, message_author=message_author, target_user=target_user)
            view = factory.get_view() if hasattr(factory, 'get_view') else None

            if view is not None:
                await ctx.send(f"Opening encyclopedia view for {target_user.display_name}", files=[factory.reload_image()], view=view)
            else:
                # Fallback: just send generated image
                await ctx.send(f"Generated encyclopedia image for {target_user.display_name}", file=convert_to_png(factory.reload_image(), "encyclopedia_view.png"))
        except Exception as e:
            await ctx.send(f"Error opening encyclopedia view: {e}")

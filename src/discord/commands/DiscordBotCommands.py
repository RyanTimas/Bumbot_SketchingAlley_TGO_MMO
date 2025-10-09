import asyncio
import sys

import aiohttp
import discord

from src.commons.CommonFunctions import convert_to_png, get_user_discord_profile_pic
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord import DiscordBot
from src.discord.buttonhandlers.EncyclopediaView import EncyclopediaView
from src.discord.buttonhandlers.player_view.PlayerProfileView import PlayerProfileView
from src.discord.buttonhandlers.TGOMMOMenuView import TGOMMOMenuView
from src.discord.image_factories.EncyclopediaImageFactory import EncyclopediaImageFactory
from src.discord.image_factories.PlayerProfilePageFactory import PlayerProfilePageFactory,  build_user_creature_collection
from src.discord.objects.CreatureRarity import MYTHICAL
from src.resources.constants.general_constants import USER_WHITELIST


def initialize_discord_commands(discord_bot: DiscordBot):
    _assign_general_discord_commands(discord_bot)
    _assign_tgo_mmo_discord_commands(discord_bot)


def _assign_general_discord_commands(discord_bot: DiscordBot):
    @discord_bot.discord_bot.command(name='shutdown')
    async def shutdown(ctx):
        """Gracefully shutdown the bot"""
        print("Shutting down bot...")

        # await delete_bot_messages(discord_bot.discord_bot, ctx.channel)
        await ctx.channel.send("Successfully shut down bot.", delete_after=5)

        # Close the Discord connection
        if discord_bot.discord_bot:
            await discord_bot.discord_bot.close()

        print("Bot successfully shut down")
        sys.exit(0)

    @discord_bot.discord_bot.command(name='bumbot')
    async def bumbot(ctx):
        if "!bumbot online" in ctx.message.content.lower():
            await ctx.message.reply("TGO MMO - Online ✔", delete_after=5)
            await ctx.message.delete(delay=5)
            return True

    @discord_bot.discord_bot.command(name='get-user-profile-pic', help="Display a user's profile picture by user ID.")
    async def get_user_profile_pic(ctx, user_id: str = None):
        target_user = ctx.guild.get_member(ctx.author.id if user_id is None else int(user_id))
        profile_pic_url = get_user_discord_profile_pic(target_user)

        # Create an embed with the avatar
        embed = discord.Embed(title=f"{target_user.name}'s Avatar")
        embed.set_image(url=profile_pic_url)

        await ctx.reply(embed=embed)

    @discord_bot.discord_bot.command(name='bumbot-test')
    async def bumbot_test(ctx):
        get_tgommo_db_handler().get_active_collections(convert_to_object=True)

        await ctx.message.delete()
        return True


def _assign_tgo_mmo_discord_commands(discord_bot: DiscordBot):
    @discord_bot.discord_bot.command(name='current-environment', help="Display the current environment.", hidden=True)
    async def current_environment(ctx):
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url

        env = discord_bot.creature_spawner_handler.current_environment
        time_of_day = "Night" if discord_bot.creature_spawner_handler.is_night_time else "Day"
        await ctx.channel.send(f"Current Environment: {env.name} ({time_of_day})", delete_after=10)


    @discord_bot.discord_bot.command(name='encyclopedia', help="List all creatures caught. Use 'verbose' for detailed stats.")
    async def encyclopedia(ctx, param1: str = None, param2: str = None, param3: str = None, param4: str = None):
        # Initialize defaults
        verbose = False
        is_server_stats = False
        target_user_id = None
        show_variants = False
        show_mythics = False

        if param1:
            if param1.lower() == "verbose":
                verbose = True
            elif param1.lower() == "server":
                is_server_stats = True
            elif param1.lower() == "variants":
                show_variants = True
            elif param1.lower() == "mythics":
                show_mythics = True
            elif param1.isdigit():
                target_user_id = int(param1)
        if param2:
            if param2.lower() == "verbose":
                verbose = True
            elif param2.lower() == "server":
                is_server_stats = True
            elif param2.lower() == "variants":
                show_variants = True
            elif param2.lower() == "mythics":
                show_mythics = True
            elif param2.isdigit():
                target_user_id = int(param2)
        if param3:
            if param3.lower() == "verbose":
                verbose = True
            elif param3.lower() == "server":
                is_server_stats = True
            elif param3.lower() == "variants":
                show_variants = True
            elif param3.lower() == "mythics":
                show_mythics = True
            elif param3.isdigit():
                target_user_id = int(param3)
        if param4:
            if param4.lower() == "verbose":
                verbose = True
            elif param4.lower() == "server":
                is_server_stats = True
            elif param4.lower() == "mythics":
                show_mythics = True
            elif param4.lower() == "variants":
                show_variants = True
            elif param4.isdigit():
                target_user_id = int(param4)

        target_user = ctx.guild.get_member(ctx.author.id if target_user_id is None else target_user_id)

        encyclopedia_img_factory = EncyclopediaImageFactory(user = target_user, environment=discord_bot.creature_spawner_handler.current_environment, verbose=verbose, is_server_page=is_server_stats, show_variants=show_variants, show_mythics=show_mythics)
        encyclopedia_img = encyclopedia_img_factory.build_encyclopedia_page_image()

        view = EncyclopediaView(encyclopedia_image_factory=encyclopedia_img_factory, is_verbose=verbose, show_variants=show_variants, show_mythics=show_mythics, message_author=ctx.author)

        await ctx.message.delete()
        await ctx.send('', files=[convert_to_png(encyclopedia_img, f'encyclopedia_test.png')], view=view)

    @discord_bot.discord_bot.command(name='player-profile', help="Shows User's . Use 'verbose' for detailed stats.")
    async def player_profile(ctx, param1: str = None, param2: str = None, param3: str = None, param4: str = None):
        # Initialize defaults
        tab_is_open = False
        open_tab = 'Team' # Default tab
        target_user_id = None

        if param1:
            if param1.lower() == "open":
                tab_is_open = True

                if not param2.isdigit():
                    open_tab = param2
                else:
                    return await ctx.followup.send("Please specify a valid tab to open (e.g., 'Team', 'Biomes', 'Collections').", delete_after=10)
            elif param1.isdigit():
                target_user_id = int(param1)
        if param3:
            open_tab = param3

        target_user = ctx.guild.get_member(ctx.author.id if target_user_id is None else target_user_id)

        player_profile_image_factory = PlayerProfilePageFactory(user_id=ctx.author.id,target_user = target_user, tab_is_open=tab_is_open, open_tab=open_tab)
        player_profile_img = player_profile_image_factory.build_player_profile_page_image()

        view = PlayerProfileView(user_id=ctx.author.id,player_profile_image_factory=player_profile_image_factory,tab_is_open=False,open_tab=open_tab)

        await ctx.message.delete()
        await ctx.send('', files=[convert_to_png(player_profile_img, f'player_profile.png')], view=view)


    @discord_bot.discord_bot.command(name='tgommo', help="Brings up the Menu for TGOMMO.")
    async def tgommo_help(ctx):
        view = TGOMMOMenuView(message_author=ctx.author, discord_bot=discord_bot)
        title_text = f'{ctx.author.mention} Welcome to the Creature Catcher Help Menu!'

        await ctx.message.delete()
        await ctx.send(title_text, files=[], view=view)

    @discord_bot.discord_bot.command(name='caught-creatures', help="Brings up list of all caught creatures.")
    async def caught_creatures(ctx):
        await build_user_creature_collection(ctx.message.author, ctx)
        await ctx.message.delete()

    # MOD COMMANDS
    @discord_bot.discord_bot.command(name='spawn_creature', help="Manually spawn a creature.", hidden=True)
    async def spawn_creature(ctx):
        if ctx.author.id not in USER_WHITELIST:
            await ctx.followup.send("You don't have permission to use this command.", delete_after=5)
            return

        creature = await discord_bot.creature_spawner_handler.creature_picker()
        await discord_bot.creature_spawner_handler.spawn_creature(creature=creature)
        await ctx.channel.send(f"Manually spawned a {creature.name}", delete_after=5)
        await ctx.message.delete()

    @discord_bot.discord_bot.command(name='spawn_every_creature', help="spawns one of every single creature for a given environment id.", hidden=True)
    async def spawn_every_creature(ctx, param1: str = None, param2: str = None, param3: str = None):
        if ctx.author.id not in USER_WHITELIST:
            await ctx.followup.send("You don't have permission to use this command.", delete_after=5)
            return

        is_mythical = "mythical" in [param1.lower() if param1 else "", param3.lower() if param3 else ""]
        environment_id = 1
        variant_no = 1

        if param1.isdigit():
            environment_id = int(param1)
            if param2 and param2.isdigit():
                variant_no = int(param2)
        elif param2.isdigit():
            environment_id = int(param2)
            if param3 and param3.isdigit():
                variant_no = int(param3)

        discord_bot.creature_spawner_handler.define_environment_and_spawn_pool(environment_id=environment_id, variant_no=variant_no)
        available_creatures = discord_bot.creature_spawner_handler.creature_spawn_pool

        for creature in available_creatures:
            if is_mythical:
                creature.img_root += '_S'
                creature.rarity = MYTHICAL

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    await discord_bot.creature_spawner_handler.spawn_creature(creature=creature)
                    await ctx.channel.send(f"Manually spawned a {creature.name}", delete_after=5)
                    break  # Success, exit retry loop
                except (discord.errors.HTTPException, aiohttp.ClientOSError) as e:
                    if attempt < max_retries - 1:
                        print(f"Network error when spawning {creature.name}: {e}. Retrying...")
                        await asyncio.sleep(2)  # Wait before retrying
                    else:
                        await ctx.channel.send(f"Failed to spawn {creature.name} after {max_retries} attempts.",delete_after=5)

    @discord_bot.discord_bot.command(name='toggle_creature_spawns', help="toggle spawning of creatures.")
    async def toggle_creature_spawns(ctx):
        if ctx.author.id not in USER_WHITELIST:
            await ctx.followup.send("You don't have permission to use this command.", delete_after=5)
            return

        result = discord_bot.creature_spawner_handler.toggle_creature_spawner(ctx)  # Get result first
        await ctx.channel.send(result, delete_after=5)




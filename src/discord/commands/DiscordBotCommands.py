import asyncio
import sys

import aiohttp
import discord

from src.commons.CommonFunctions import convert_to_png, get_user_discord_profile_pic
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord import DiscordBot
from src.discord.buttonhandlers.EncyclopediaView import EncyclopediaView
from src.discord.deprecated.EncyclopediaPageButton import EncyclopediaPageShiftView
from src.discord.image_factories.EncyclopediaImageFactory import EncyclopediaImageFactory
from src.discord.objects.CreatureRarity import MYTHICAL


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
            await ctx.message.reply("Project: Creature Catcher - Online ✔", delete_after=5)
            await ctx.message.delete(delay=5)
            return True

    @discord_bot.discord_bot.command(name='get_user_profile_pic', help="Display a user's profile picture by user ID.")
    async def get_user_profile_pic(ctx, user_id: str = None):
        target_user = ctx.guild.get_member(ctx.author.id if user_id is None else int(user_id))
        profile_pic_url = get_user_discord_profile_pic(target_user)

        # Create an embed with the avatar
        embed = discord.Embed(title=f"{target_user.name}'s Avatar")
        embed.set_image(url=profile_pic_url)

        await ctx.reply(embed=embed)


def _assign_tgo_mmo_discord_commands(discord_bot: DiscordBot):
    @discord_bot.discord_bot.command(name='spawn_creature', help="Manually spawn a creature.")
    async def spawn_creature(ctx):
        creature = await discord_bot.creature_spawner_handler.creature_picker()
        await discord_bot.creature_spawner_handler.spawn_creature(creature=creature)
        await ctx.channel.send(f"Manually spawned a {creature.name}", delete_after=5)


    @discord_bot.discord_bot.command(name='toggle_creature_spawns', help="toggle spawning of creatures.")
    async def toggle_creature_spawns(ctx):
        result = discord_bot.creature_spawner_handler.toggle_creature_spawner(ctx)  # Get result first
        await ctx.channel.send(result, delete_after=5)


    @discord_bot.discord_bot.command(name='current_environment', help="Display the current environment.")
    async def current_environment(ctx):
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url

        env = discord_bot.creature_spawner_handler.current_environment
        time_of_day = "Night" if discord_bot.creature_spawner_handler.is_night_time else "Day"
        await ctx.channel.send(f"Current Environment: {env.name} ({time_of_day})", delete_after=10)


    @discord_bot.discord_bot.command(name='caught_creatures', help="List all creatures caught. Use 'verbose' for detailed stats.")
    async def caught_creatures(ctx, param1: str = None, param2: str = None, param3: str = None, param4: str = None):
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

        view = EncyclopediaView(encyclopedia_image_factory=encyclopedia_img_factory, is_verbose=verbose, show_variants=show_variants, show_mythics=show_mythics, message_author=ctx.author.id)

        await ctx.reply('', files=[convert_to_png(encyclopedia_img, f'encyclopedia_test.png')], view=view)


    @discord_bot.discord_bot.command(name='spawn_every_creature', help="spawns one of every single creature for a given environment id.")
    async def spawn_every_creature(ctx, param1: str = None):
        available_creatures = discord_bot.creature_spawner_handler.creature_spawn_pool

        for creature in available_creatures:
            if param1 and param1.lower() == 'mythical':
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




import sys

import discord

from src.commons.CommonFunctions import convert_to_png, get_user_discord_profile_pic
from src.database.handlers.DatabaseHandler import get_tgommo_db_handler
from src.discord import DiscordBot
from src.discord.buttonhandlers.EncyclopediaPageButton import EncyclopediaPageShiftView
from src.discord.image_factories.EncyclopediaImageFactory import EncyclopediaImageFactory


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

        response = generate_response(user_id=target_user.id, response="", verbose=verbose)
        view = EncyclopediaPageShiftView(encyclopedia_image_factory=encyclopedia_img_factory, current_page=encyclopedia_img_factory.page_num, total_pages=encyclopedia_img_factory.total_pages, is_verbose=verbose, show_variants=show_variants, show_mythics=show_mythics, message_author=ctx.author.id)

        await ctx.reply(response, files=[convert_to_png(encyclopedia_img, f'encyclopedia_test.png')], view=view)



def generate_response(user_id, response="", verbose=False):
    creatures = get_tgommo_db_handler().get_all_creatures_caught_by_user(user_id=user_id)

    for creature in creatures:
        creature_name = creature[1]
        variant_name = creature[2]
        dex_no = creature[3]
        variant_no = creature[4]
        total_catches = creature[5]

        creature_is_locked = False if total_catches > 0 else True

        if not creature_is_locked:
            response += f"#{dex_no}"
            if variant_name != '':
                letter = chr(64 + int(variant_no)) if 1 <= int(variant_no) <= 26 else f"#{dex_no}"
                response += f"{letter}"
            else:
                response += f"‎"
            response += f"\t {creature_name}"
            response += f" ({variant_name})" if variant_name != '' else ""
            response += f" Total Caught: {total_catches}"

            for i in range(total_catches // 10):
                response += "⭐"

            response += "\n"

    return response





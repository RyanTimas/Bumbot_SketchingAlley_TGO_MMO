import sys
import random
from importlib.metadata import files

import discord

from src.commons.CommonFunctions import convert_to_png
from src.database.handlers.DatabaseHandler import DatabaseHandler, get_db_handler, get_tgommo_db_handler
from src.discord import DiscordBot
from src.discord.image_factories.DexIconFactory import DexIconFactory
from src.discord.objects.CreatureRarity import COMMON
from src.resources.constants.TGO_MMO_constants import TGOMMO_RARITY_COMMON


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
        if user_id is None:
            # If no user ID provided, use the command author
            target = ctx.author
        else:
            try:
                # Convert string ID to integer
                user_id = int(user_id)
                # Fetch the user from the ID
                target = ctx.guild.get_member(user_id)
            except (ValueError, discord.NotFound, discord.HTTPException):
                await ctx.reply("Invalid user ID or user not found.")
                return

        # Get the avatar URL (note: fetch_user returns a User, not Member, so display_avatar might not be available)
        avatar_url = target.display_avatar.url if hasattr(target,
                                                          'display_avatar') else target.avatar.url if target.avatar else target.default_avatar.url

        # Create an embed with the avatar
        embed = discord.Embed(title=f"{target.name}'s Avatar")
        embed.set_image(url=avatar_url)

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
    async def caught_creatures(ctx, option: str = None):
        verbose = option == "verbose"

        dex_icons, response = get_dex_icons(ctx.author.id, f"**{ctx.author.display_name}'s Caught Creatures:**\n", verbose)
        await ctx.reply(response, files=dex_icons if len(dex_icons) > 0 else None)


def get_dex_icons(user_id, response="", verbose=False):
    creatures = get_tgommo_db_handler().get_all_creatures_caught_by_user(user_id=user_id)
    imgs = []

    for creature in creatures:
        creature_name = creature[1]
        variant_name = creature[2]
        dex_no = creature[3]
        variant_no = creature[4]
        rarity = get_tgommo_db_handler().get_creature_rarity_for_environment(creature_id=creature[0], environment_id=1)
        total_catches = creature[5]
        total_mythical_catches = creature[6]

        creature_is_locked = False if total_catches > 0 else True

        dex_icon = DexIconFactory(creature_name=creature_name, dex_no=dex_no, variant_no=variant_no, rarity=rarity, creature_is_locked=creature_is_locked, show_stats=verbose, total_catches=total_catches, total_mythical_catches=total_mythical_catches)
        dex_icon_img = dex_icon.generate_dex_entry_image()

        imgs.append(convert_to_png(dex_icon_img, f'creature_icon_{creature[3]}_{variant_no}.png'))

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

    return imgs, response





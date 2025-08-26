import sys
import random
import discord

from src.database.handlers.DatabaseHandler import DatabaseHandler, get_db_handler, get_tgommo_db_handler
from src.discord import DiscordBot


def assign_general_discord_commands(discord_bot: DiscordBot):
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


def assign_tgo_mmo_discord_commands(discord_bot: DiscordBot):
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
        env = discord_bot.creature_spawner_handler.current_environment
        time_of_day = "Night" if discord_bot.creature_spawner_handler.is_night_time else "Day"
        await ctx.channel.send(f"Current Environment: {env.name} ({time_of_day})", delete_after=10)

    @discord_bot.discord_bot.command(name='caught_creatures', help="List all creatures caught.")
    async def caught_creatures(ctx):
        creatures = get_tgommo_db_handler().get_all_creatures_caught_by_user(user_id=ctx.author.id)


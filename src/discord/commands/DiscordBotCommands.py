import sys
import random
import discord

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


    @discord_bot.discord_bot.command(name='toggle_creature_spawns', help="toggle spawning of creatures.")
    async def toggle_creature_spawns(ctx):
        result = discord_bot.toggle_creature_spawns()  # Get result first
        await ctx.channel.send(result, delete_after=5)
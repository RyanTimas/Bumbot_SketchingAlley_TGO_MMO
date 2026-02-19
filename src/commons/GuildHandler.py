import discord
from src.resources.constants.general_constants import TGOMMO_ACTIVE_SERVER_TOKEN

_guild_instance = None

def get_guild():
    """Get the singleton guild instance"""
    global _guild_instance
    if _guild_instance is None:
        raise RuntimeError("Guild not initialized. Call set_guild() first.")
    return _guild_instance

def set_guild(bot: discord.Client):
    """Initialize the guild singleton from bot instance"""
    global _guild_instance
    _guild_instance = bot.get_guild(TGOMMO_ACTIVE_SERVER_TOKEN)
    if _guild_instance is None:
        raise RuntimeError(f"Guild with ID {TGOMMO_ACTIVE_SERVER_TOKEN} not found")
    return _guild_instance
# Retry decorator for handling SSL errors. Retries the decorated function up to max_retries times with a delay between attempts if an SSL error occurs.
import asyncio
import functools
import ssl

import aiohttp
import discord
from discord import app_commands
import functools
import time
import asyncio
from typing import Callable, Optional, Any

from src.commons.CommonFunctions import check_if_user_can_interact_with_view
from src.resources.constants.general_constants import DISCORD_USER_WHITELIST

# Retry decorator for handling SSL errors. Retries the decorated function up to max_retries times with a delay between attempts if an SSL error occurs.
def retry_on_ssl_error(max_retries=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except discord.errors.InteractionResponded:
                    # Interaction already responded to, so don't retry
                    return
                except aiohttp.client_exceptions.ClientOSError as e:
                    if "SSL" in str(e) and retries < max_retries - 1:
                        retries += 1
                        await asyncio.sleep(delay)
                    else:
                        # If we've exhausted retries or it's not an SSL error, re-raise
                        raise
        return wrapper
    return decorator

# Decorator to restrict command usage to a whitelist of Discord user IDs. If the user is not in the whitelist, they receive an ephemeral message indicating they don't have permission.
def admin_only():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id not in DISCORD_USER_WHITELIST:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True, delete_after=5)
            return False
        return True
    return app_commands.check(predicate)

# Decorator to guard interactions with a lock to prevent multiple simultaneous interactions. It checks if the user can interact with the view and retries the interaction if an SSL error occurs, with an optional deferred response.
def interaction_guard(self=None, max_retries=3, delay=1, defer_response=True):
    def decorator(func):
        async def wrapper(interaction):
            if not self:
                return await func(interaction)

            if await check_if_user_can_interact_with_view(interaction, self.interaction_lock, getattr(self, 'message_author', None).user_id):
                async with self.interaction_lock:
                    if defer_response:
                        await interaction.response.defer()

                    for attempt in range(max_retries):
                        try:
                            return await func(interaction)
                        except ssl.SSLError as e:
                            if attempt == max_retries - 1:
                                raise e
                            await asyncio.sleep(delay)
        return wrapper
    return decorator

# Decorator to measure and log the execution time of both synchronous and asynchronous functions. It accepts an optional label for logging and a custom logger function.
def measure_execution_time(label: Optional[str] = None, logger: Optional[Callable[[str], None]] = None):
    logger = logger or print

    def decorator(func: Callable):
        is_coro = asyncio.iscoroutinefunction(func)

        if is_coro:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start = time.perf_counter()
                try:
                    return await func(*args, **kwargs)
                finally:
                    elapsed = time.perf_counter() - start
                    logger(f"{label or func.__name__} execution time: {elapsed:.6f} seconds")
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    elapsed = time.perf_counter() - start
                    logger(f"{label or func.__name__} execution time: {elapsed:.6f} seconds")
            return sync_wrapper

    return decorator
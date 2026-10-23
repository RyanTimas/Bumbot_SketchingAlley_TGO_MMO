import asyncio
import functools
import threading
from typing import Any, Callable


_BLOCKING_WORK_LOCK = threading.RLock()

# This function is used to run a blocking function while holding a process-wide lock to prevent concurrent execution of legacy code that shares mutable SQLite connection and cursor fields.
def _run_locked(function: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    with _BLOCKING_WORK_LOCK:
        return function(*args, **kwargs)

# This function is an asynchronous wrapper that runs a blocking function in a separate thread while ensuring that only one such function can run at a time across the entire process. It uses the asyncio event loop to run the blocking function in an executor, allowing other asynchronous tasks to continue running without being blocked.
async def run_serialized_blocking(function: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    loop = asyncio.get_running_loop()
    bound_call = functools.partial(_run_locked, function, args, kwargs)
    return await loop.run_in_executor(None, bound_call)


"""
    description: make sync function async & wrapper with same syntax for sync and async
      functions
    name: await_utils
    version: 0.0.0
"""
import asyncio
import concurrent.futures


async def await_sync(func, *args, highcpu=False):
    loop = asyncio.get_event_loop()
    if not highcpu:
        return await loop.run_in_executor(None, func, *args)
    with concurrent.futures.ProcessPoolExecutor() as pool:
        return await loop.run_in_executor(pool, func, *args)


async def await_if_awaitable(value):
    if hasattr(value, '__await__'):
        return await value
    else:
        return value

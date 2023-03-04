"""
    description: call function with schedule by cron
    name: cron
    needs_pip:
      croniter: croniter
    version: 0.1.0
"""
import asyncio
import datetime
import logging
from croniter import croniter

logger = logging.getLogger(__name__.split('/')[-1])

TZ_MOSCOW = datetime.timezone(datetime.timedelta(hours=3))

cron_task = None
cron_jobs = []


def cron_add_job(func, cron):
    nonlocal cron_jobs
    croniter(cron, datetime.datetime.now(TZ_MOSCOW))  # check if cron is valid
    cron_jobs.append([func, cron])
    if cron_task is not None:
        cron_stop_working()
    cron_start_working()


async def cron_work():
    while True:
        now = datetime.datetime.now(TZ_MOSCOW)
        for [func, cron] in cron_jobs:
            if croniter.match(cron, now):
                logger.info(f"running {func}")
                if asyncio.iscoroutinefunction(func):
                    asyncio.create_task(func())
                else:
                    func()
        sleep_until = None
        for [func, cron] in cron_jobs:
            next_time = croniter(cron, now).get_next(datetime.datetime)
            if sleep_until is None or next_time < sleep_until:
                sleep_until = next_time
        if sleep_until is None:
            break
        sleep_time = (sleep_until - now).total_seconds()
        logger.info(f"sleeping for {sleep_time} seconds")
        await asyncio.sleep(sleep_time)


def cron_start_working():
    nonlocal cron_task
    cron_task = asyncio.create_task(cron_work())


def cron_stop_working():
    nonlocal cron_task
    cron_task.cancel()


__all__ = ['cron_add_job']

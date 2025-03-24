"""
    name: channel_join_requests
    once: false
    origin: tgpy://modules/channel_join_requests
    priority: 1700000004
"""
from multiprocessing.managers import Value

logger = ConsoleLogger(f"{__name__.split('/')[-1]}\t| ")

import telethon
import tgpy.api
from cache import AsyncTTL


@AsyncTTL(time_to_live=60 * 60 * 24)
async def get_channel_name(id):
    channel = await client.get_entity(telethon.types.PeerChannel(id))
    return channel.title


@AsyncTTL(time_to_live=60 * 60 * 24)
async def get_user_name(id):
    user = await client.get_entity(telethon.types.PeerUser(id))
    if user.username:
        return '@' + user.username
    return f'<a href="tg://user?id={user.id}">{user.first_name}</a>'


def get_config():
    return tgpy.api.config.get('channel_join_requests', default={})


def set_config(config):
    return tgpy.api.config.set('channel_join_requests', config)


@client.on(telethon.events.Raw)
async def join_request_handler(update):
    if not isinstance(update, telethon.types.UpdatePendingJoinRequests):
        return
    logger.print(f'channel_id={update.peer.channel_id} recent_requesters={update.recent_requesters}')
    channel_id = update.peer.channel_id
    config = get_config()
    if channel_id not in config:
        return
    old_requesters = config[channel_id]
    recent_requesters = update.recent_requesters
    config[channel_id] = recent_requesters
    set_config(config)

    new_user_names = []
    full_channel = False
    for user_id in set(recent_requesters) - set(old_requesters):
        try:
            new_user_names.append(await get_user_name(user_id))
        except ValueError:
            if full_channel:
                logger.print(f'Cant get username of {user_id}')
                continue
            logger.print(f'Full channel request channel_id={channel_id}')
            await client(telethon.functions.channels.GetFullChannelRequest(channel_id))
            full_channel = True
            try:
                new_user_names.append(await get_user_name(user_id))
            except ValueError:
                logger.print(f'Cant get username of {user_id}')

    new_user_names = [await get_user_name(user_id) for user_id in set(recent_requesters) - set(old_requesters)]
    if len(new_user_names) > 0:
        channel_name = await get_channel_name(channel_id)
        message = '\n'.join([f'New joining requests in channel "{channel_name}"', *new_user_names])
        await pet_bot.send(message)


def channel_join_requests_add(channel_id):
    logger.print("Adding channel", channel_id)
    config = get_config()
    if channel_id not in config:
        config[channel_id] = {}
        set_config(config)
    return f'Tracked channels: {list(config.keys())}'


def channel_join_requests_remove(channel_id):
    logger.print("Removing channel", channel_id)
    config = get_config()
    if channel_id in config:
        config.pop(channel_id)
        set_config(config)
    return f'Tracked channels: {list(config.keys())}'


__all__ = ['channel_join_requests_add', 'channel_join_requests_remove']

"""
    name: track_last_seen
    once: false
    origin: tgpy://modules/track_last_seen
    priority: 1700000005
"""
logger = ConsoleLogger(f"{__name__.split('/')[-1]}\t| ")

import asyncio
import tgpy.api
import telethon
from cache import AsyncTTL


def get_config():
    config = tgpy.api.config.get('track_last_seen', {'chat_id': None, 'user_ids': []})
    if config.get('chat_id') is None:
        config['chat_id'] = int(logger.input('Enter chat_id: '))
        set_config(config)
    return config


def set_config(config):
    tgpy.api.config.set('track_last_seen', config)


@AsyncTTL(time_to_live=60 * 60 * 24)
async def get_user_name(id):
    me = await client.get_me()
    if id == me.id:
        return me.first_name

    user = await client.get_entity(telethon.types.PeerUser(id))
    if user.username:
        return '@' + user.username
    return f'<a href="tg://user?id={user.id}">{user.first_name}</a>'


async def track_last_seen_add(*user_entities, ignore_if_exists=True):
    logger.print("Adding", user_entities)
    config = get_config()
    new_ids = []
    for user_entity in user_entities:
        user_id = user_entity if isinstance(user_entity, int) else (await client.get_entity(user_entity)).id
        if user_id not in config['user_ids']:
            config['user_ids'].append(user_id)
            new_ids.append(user_id)
        elif not ignore_if_exists:
            new_ids.append(user_id)
    set_config(config)

    if len(new_ids) == 0:
        return "Added 0 users"

    @client.on(telethon.events.UserUpdate(chats=new_ids, func=lambda e: e.status))
    async def user_update_event_handler(event):
        name = await get_user_name(event.user_id)

        if isinstance(event.status, telethon.types.UserStatusOnline):
            text = f'{name} online'
        elif isinstance(event.status, telethon.types.UserStatusOffline):
            text = f'{name} disconnected'
        else:
            text = f'{name} {event.status.__class__.__name__}'
        await pet_bot.send(text, chat_id=config['chat_id'])

    return f"Added {len(new_ids)} users"


async def track_last_seen_remove(*user_entities):
    logger.print("Removing", user_entities)
    config = get_config()
    cnt = 0
    for user_entity in user_entities:
        user_id = user_entity if isinstance(user_entity, int) else (await client.get_entity(user_entity)).id
        if user_id not in config['user_ids']:
            continue
        cnt += 1
        config['user_ids'].remove(user_id)
    set_config(config)

    return f"Removed {cnt} users\n\nChanges will be applied after restart()"


asyncio.create_task(track_last_seen_add(*get_config()['user_ids'], ignore_if_exists=False))

__all__ = ['track_last_seen_add', 'track_last_seen_remove']

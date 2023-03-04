"""
    description: get username/first name/title of telethon entity object
    name: tg_name
    version: 0.0.0
"""
import telethon.tl.types


def get_name(user, try_username=True):
    if isinstance(user, telethon.tl.types.Channel):
        return f'"{user.title}"'
    if try_username and user.username:
        return '@' + user.username
    return f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

"""
    description: get stats of logged in pixiv user
    name: pixiv
    needs:
      config_loader: 0.0.0
      dot: 0.2.0
    needs_pip:
      pixivpy_async: PixivPy-Async
    version: 0.1.0
"""
import pixivpy_async
import asyncio
import random
import time

import logging

logger = logging.getLogger(__name__.split('/')[-1])

REQUEST_ATTEMPTS = 3
ACCESS_TOKEN_TIMEOUT = 60 * 60 - 5


async def randSleep(base=0.1, rand=0.5):
    await asyncio.sleep(base + rand * random.random())


class AutoLoginAPI:
    def __init__(self, refresh_token=None, **requests_kwargs):
        super().__init__(**requests_kwargs)
        self.REFRESH_TOKEN = refresh_token
        self.api = pixivpy_async.AppPixivAPI(**requests_kwargs)
        self.last_login = 0

    def __getattr__(self, item):
        api_item = self.api.__getattribute__(item)
        logger.info('get api attr: ' + str(item))
        if not asyncio.iscoroutinefunction(api_item):
            return api_item

        async def wrapper(*args, **kwargs):
            e = None
            if 'req_auth' not in kwargs:
                kwargs['req_auth'] = True

            if self.is_expired_token():
                await self.login()
                await randSleep()

            for _ in range(REQUEST_ATTEMPTS):
                try:
                    return await api_item(*args, **kwargs)
                except (pixivpy_async.error.NoTokenError, pixivpy_async.error.NoLoginError) as e:
                    logger.error('Error while calling ' + str(item))
                    logger.error(e)
                    await self.login()
                    await randSleep()
            raise e

        return wrapper

    def is_expired_token(self):
        return time.time() - self.last_login > ACCESS_TOKEN_TIMEOUT

    async def login(self):
        logger.info('logging in...')
        await self.api.login(refresh_token=self.REFRESH_TOKEN)
        self.last_login = time.time()


class PixivUser:
    """
        use with dot:
        .pixiv = .pixiv stats
        .pixiv stats = .pixiv stats partial
        .pixiv stats partial - get total illusts, views, bookmarks and followers
        .pixiv status full - partial + max views and bookmarks
    """

    def __init__(self, user_id, refresh_token=None):
        self.USER_ID = user_id
        self.api = AutoLoginAPI(refresh_token)
        self.user_details = None

    async def iterate_request_offset(self, api_request, query_params):
        while query_params is not None:
            r = await api_request(**query_params)
            yield r
            query_params = self.api.parse_qs(r['next_url'])
            await randSleep()

    async def get_all_followers(self):
        result = []
        async for r in self.iterate_request_offset(self.api.user_follower, {"user_id": self.USER_ID}):
            result.extend(r['user_previews'])
        return result

    async def get_all_illusts(self):
        result = []
        async for r in self.iterate_request_offset(self.api.user_illusts, {"user_id": self.USER_ID}):
            result.extend(r['illusts'])
        return result

    async def get_user_details(self):
        if self.user_details is None:
            self.user_details = await self.api.user_detail(self.USER_ID)
        return self.user_details

    async def illusts_stats(self):
        illusts = await self.get_all_illusts()
        views = 0
        bookmarks = 0
        max_views = 0
        max_bookmarks = 0
        for illust in illusts:
            views += illust['total_view']
            bookmarks += illust['total_bookmarks']
            max_views = max(max_views, illust['total_view'])
            max_bookmarks = max(max_bookmarks, illust['total_bookmarks'])
        return {
            'Total illusts': len(illusts),
            'Total views': views,
            'Total bookmarks': bookmarks,
            'Max views': max_views,
            'Max bookmarks': max_bookmarks,
        }

    async def followers_stats(self):
        followers = await self.get_all_followers()
        return {
            'Total followers': len(followers)
        }

    async def user_stats(self):
        r = await self.get_user_details()
        user_name = r['user']['name']
        user_url = f"https://pixiv.net/en/users/{r['user']['id']}"
        return {
            "Username": user_name,
            "URL": user_url
        }

    async def text_stats(self, keys):
        user = await self.user_stats()
        message = f"🎨 Pixiv stats of <a href='{user['URL']}'>{user['Username']}</a>"
        stats = await self.illusts_stats() | await self.followers_stats()
        for key in keys:
            if key in stats:
                message += f"\n{key}: {stats[key]}"
        return message


@dot('pixiv')
async def pixiv_dot_handler(text=''):
    commands = list(filter(bool, '\n'.join(filter(lambda line: not line.startswith('>'), text.split('\n'))).split()))
    tree = {
        'stats': {
            'partial': (
                pixiv_user.text_stats, [['Total illusts', 'Total views', 'Total bookmarks', 'Total followers']]
            ),
            'full': (
                pixiv_user.text_stats,
                [['Total illusts', 'Total views', 'Total bookmarks', 'Max views', 'Max bookmarks', 'Total followers']]
            )
        }
    }
    tree['stats'][''] = tree['stats']['partial']
    tree[''] = tree['stats']

    command_index = 0
    while isinstance(tree, dict):
        c = ''
        if command_index < len(commands):
            c = commands[command_index]
            command_index += 1
        tree = tree.get(c)
        if tree is not None:
            continue
        return "Unknown command"

    if isinstance(tree, dict):
        return "Unknown command"
    ctx.is_manual_output = True
    ans = await tree[0](*tree[1])
    await ctx.msg.edit(ans)


config = ModuleConfig('pixiv', ('user_id', 'refresh_token'))
pixiv_user = PixivUser(config.user_id, config.refresh_token)

__all__ = ['pixiv_user', 'PixivUser']

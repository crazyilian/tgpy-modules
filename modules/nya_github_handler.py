"""
    name: nya_github_handler
    description: github source handler for Nya
    needs:
      nya: 0.32.6
    needs_pip:
      aiohttp: aiohttp
      github: pygithub
      cachetools: cachetools
    version: 0.4.0
"""
from urllib.parse import urlparse
import tgpy.api
import aiohttp
import github
from github.GithubObject import NotSet
import cachetools.func
import asyncio


async def await_sync(func, *args):
    return await asyncio.get_event_loop().run_in_executor(None, func, *args)


class GithubHandler:
    """
        It is obligatory to set your github token if you want to access private repos.
    """

    def __init__(self):
        self.session = None
        self.__create_session(self.get_token())

    def __create_session(self, token):
        if self.session:
            self.session.close()
        self.session = aiohttp.ClientSession(headers={'Authorization': f'Token {token}'} if token else {})
        self.gh = github.Github(token)

    @cachetools.func.ttl_cache(maxsize=128, ttl=60)
    def __get_ttl_repo_sync(self, repo_str):
        return self.gh.get_repo(repo_str)

    async def __get_ttl_repo(self, repo_str):
        return await await_sync(self.__get_ttl_repo_sync, repo_str)

    async def __get_contents(self, path, branch, repo):
        return await await_sync(repo.get_contents, path, branch)

    @staticmethod
    def __parse_src(src):
        """Split repo, branch and file path from url"""
        path = urlparse(src).path.strip('/').split('/')
        repo = path[0] + '/' + path[1]
        branch = path[3] if len(path) >= 3 else NotSet
        file = '/'.join(path[4:])
        return repo, branch, file

    async def handler(self, src):
        """Get file content by url"""
        repo_str, branch, path = self.__parse_src(src)
        try:
            repo = await self.__get_ttl_repo(repo_str)
            return (await self.__get_contents(path, branch, repo)).decoded_content.decode('utf-8')
        except github.RateLimitExceededException:
            download_url = f'https://raw.githubusercontent.com/{repo_str}/{branch}/{path}'
            return await self.handler_raw(download_url)

    async def handler_raw(self, src):
        """Get file content by raw url"""
        return await (await self.session.get(src)).text()

    def get_token(self):
        """Get you current access token"""
        return tgpy.api.config.get(f'nya_github_handler.token', None)

    def set_token(self, token=None):
        """Set access token (https://github.com/settings/tokens)"""
        self.__create_session(token)
        tgpy.api.config.set(f'nya_github_handler.token', token)


nya.github_handler = GithubHandler()
nya.add_source_handler(('https', 'github.com'), nya.github_handler.handler)
nya.add_source_handler(('https', 'raw.githubusercontent.com'), nya.github_handler.handler_raw)

__all__ = []

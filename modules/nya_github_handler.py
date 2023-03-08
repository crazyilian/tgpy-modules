"""
    name: nya_github_handler
    description: github source handler for Nya
    needs:
      nya: 0.32.6
    needs_pip:
      aiohttp: aiohttp
    version: 0.3.0
"""
from urllib.parse import urlparse
import tgpy.api
import aiohttp


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

    async def _handler(self, src):
        """Get file content by url"""
        path = urlparse(src).path.strip('/').split('/')
        path.pop(2)
        download_url = f'https://raw.githubusercontent.com/' + '/'.join(path)
        return await self._raw_handler(download_url)

    async def _raw_handler(self, src):
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
nya.add_source_handler(('https', 'github.com'), nya.github_handler._handler)
nya.add_source_handler(('https', 'raw.githubusercontent.com'), nya.github_handler._raw_handler)

__all__ = []

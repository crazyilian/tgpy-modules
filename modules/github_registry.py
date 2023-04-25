"""
    name: github_registry
    description: share source of github repo/dir/file in format of nya registry
    needs:
      nya: 0.32.6
    needs_pip:
      github: pygithub
      cachetools: cachetools
      lxml: lxml
      aiohttp: aiohttp
    version: 0.1.1
"""

from urllib.parse import urlparse
import tgpy.api
import github
from github.ContentFile import ContentFile
from github.GithubObject import NotSet
import os.path
from telethon.tl.types import MessageEntityCode
import cachetools.func
import aiohttp
import lxml.html
import asyncio


async def await_sync(func, *args):
    return await asyncio.get_event_loop().run_in_executor(None, func, *args)


class GithubWrapper:
    def __init__(self, token=None):
        self.gh = github.Github(token)
        self.session = aiohttp.ClientSession(headers={'Authorization': f'Token {token}'} if token else {})

    @cachetools.func.ttl_cache(maxsize=128, ttl=30)
    def get_repo_unsafe_sync(self, repo):
        return self.gh.get_repo(repo, False)

    async def get_repo_unsafe(self, repo):
        return await await_sync(self.get_repo_unsafe_sync, repo)

    async def get_repo(self, repo, use_api=True):
        try:
            assert use_api
            return await self.get_repo_unsafe(repo)
        except (github.RateLimitExceededException, AssertionError):
            return repo

    async def request_text(self, url):
        return await (await self.session.get(url)).text()

    async def request_lxml(self, url):
        return lxml.html.fromstring(await self.request_text(url))

    async def get_parsed_default_branch(self, repo):
        lxml_root = await self.request_lxml(f'https://github.com/{repo}')
        for element in lxml_root.xpath("//summary//span[contains(@class, 'css-truncate-target')]"):
            return element.text

    async def get_default_branch(self, repo, use_api=True):
        if isinstance(repo, str):
            try:
                assert use_api
                repo = await self.get_repo_unsafe(repo)
                return repo.default_branch
            except (github.RateLimitExceededException, AssertionError):
                return await self.get_parsed_default_branch(repo)
        else:
            return repo.default_branch

    async def get_raw_file(self, path, ref, repo) -> dict:
        download_url = f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"
        resp = await self.session.get(download_url)
        assert resp.status == 200
        return {
            'type': 'file',
            'path': path,
            'code': await resp.text(),
            'download_url': download_url,
            'html_url': f'https://github.com/{repo}/blob/{ref}/{path}'
        }

    async def get_parsed_dir(self, path, ref, repo) -> list[dict]:
        html_url = f'https://github.com/{repo}/tree/{ref}/{path}'
        lxml_root = await self.request_lxml(html_url)
        files = []
        for element in lxml_root.xpath(   # old style
                "//div[contains(@class, 'Box')]"
                "//div[contains(@class, 'Details')]"
                "//*[name()='svg' and contains(@aria-label, 'Directory')]"
                "/../..//a[contains(@class, 'js-navigation-open')]") + \
                lxml_root.xpath(    # new style
                "//table[contains(@aria-labelledby, 'folders-and-files')]"
                "//div[contains(@class, 'sr-only') and contains(text(), '(Directory)')]"
                "/..//a"):
            name = element.text
            files.append({
                'type': 'dir',
                'path': (path + '/' + name).strip('/'),
                'html_url': html_url
            })
        return files

    async def get_api_contents(self, path, ref, repo):
        if isinstance(repo, str):
            repo = await self.get_repo_unsafe(repo)
        contents = await await_sync(repo.get_contents, path, ref)
        if isinstance(contents, ContentFile):
            contents = [contents]
        res = []
        for content in contents:
            isfile = content.type == 'file'
            res.append({
                'type': content.type,
                'path': content.path,
                'code': content.decoded_content.decode('utf-8') if isfile else None,
                'download_url': content.download_url if isfile else None,
                'html_url': content.html_url
            })
        return res

    async def get_parsed_contents(self, path, ref, repo):
        if ref == NotSet or ref is None:
            ref = await self.get_default_branch(repo, use_api=False)
        if not isinstance(repo, str):
            repo = repo.full_name
        try:
            return [await self.get_raw_file(path, ref, repo)]
        except:
            return await self.get_parsed_dir(path, ref, repo)

    async def get_contents(self, path, ref, repo, use_api=True):
        try:
            assert use_api
            return await self.get_api_contents(path, ref, repo)
        except (github.RateLimitExceededException, AssertionError):
            if use_api:
                print('API failed, trying to parse', path)
            return await self.get_parsed_contents(path, ref, repo)


class GithubRegistry:
    """
        Shortcut: gh_reg = github_registry

        It is RECOMMENDED to set token if you want to use other features. Without token you have
          limit of 60 api requests per hour (with token it is 5000 requests). If limit is exceeded
          features will try to parse github website, and this mostly only works with public repos.
    """

    def __init__(self):
        self.ghw = GithubWrapper(self.get_token())

    @staticmethod
    def __parse_src(src):
        """Split repo, branch and file path from url"""
        path = urlparse(src).path.strip('/').split('/')
        repo = path[0] + '/' + path[1]
        branch = path[3] if len(path) >= 3 else NotSet
        file = '/'.join(path[4:])
        return repo, branch, file

    def get_token(self):
        """Get you current access token"""
        return tgpy.api.config.get(f'share_github_registry.token', None)

    def set_token(self, token=None):
        """Set access token (https://github.com/settings/tokens)"""
        self.ghw = GithubWrapper(token)
        tgpy.api.config.set(f'share_github_registry.token', token)

    async def get_sources(self, src, use_raw=False, recursive=True, extensions=('.py',), use_api=True):
        """Return url of files in directory in github repo (nya registry format)"""
        repo, branch, path = self.__parse_src(src)
        repo = await self.ghw.get_repo(repo, use_api=use_api)
        contents = await self.ghw.get_contents(path, branch, repo, use_api=use_api)
        registry = {}
        while contents:
            content = contents.pop(0)
            if content['type'] == 'file':
                extension = os.path.splitext(content['path'])[1]
                if extension in extensions:
                    try:
                        module_name = nya._Nya__parse(content['code'])[0]
                        if use_raw or module_name in ('nya_github_handler', 'nya_gitlab_handler'):
                            url = content['download_url']
                        else:
                            url = content['html_url']
                        registry[module_name] = url
                    except:
                        print(f"ERROR: Not a module: {content['html_url']}")
            elif content['type'] == "dir":
                if recursive:
                    contents.extend(await self.ghw.get_contents(content['path'], branch, repo, use_api=use_api))
        ans = '"""\n    sources:\n' + "\n".join([f'        {name}: "{registry[name]}"' for name in registry]) + '\n"""'
        return ans

    async def share(self, src, use_raw=False, recursive=True, extensions=('.py',), use_api=True):
        """Share url of files in directory in github repo (nya registry format)"""
        ans = await self.get_sources(src, use_raw, recursive, extensions, use_api)
        await ctx.msg.respond(ans, formatting_entities=[MessageEntityCode(0, len(ans.encode('utf-16-le')) // 2)])

    async def __call__(self, *args, **kwargs):
        return await self.share(*args, **kwargs)


github_registry = GithubRegistry()
gh_reg = github_registry

__all__ = ['github_registry', 'gh_reg']

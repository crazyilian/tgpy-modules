"""
    name: nya_github_handler
    description: github source handler for Nya
    needs:
      nya: 0.32.6
    needs_pip:
      github: pygithub
    version: 0.1.0
"""
from urllib.parse import urlparse
import tgpy.api
import github
from github.ContentFile import ContentFile
from github.GithubObject import NotSet
import os.path
from telethon.tl.types import MessageEntityCode


class GithubHandler:
    """
        It is STRONGLY RECOMMENDED to set your github token, otherwise you have limit only 60 requests per hour.
        For authenticated users there are 5000 requests per hour limit.
    """

    def __init__(self):
        self.gh = github.Github(self.get_token())

    @staticmethod
    def parse_src(src):
        """Split repo, branch and file path from url"""
        path = urlparse(src).path.strip('/').split('/')
        repo = path[0] + '/' + path[1]
        branch = path[3] if len(path) >= 3 else NotSet
        file = '/'.join(path[4:])
        return repo, branch, file

    async def handler(self, src):
        """Get file content by url"""
        repo, branch, file = self.parse_src(src)
        return self.gh.get_repo(repo).get_contents(file, branch).decoded_content.decode('utf-8')

    def get_token(self):
        """Get you current access token"""
        return tgpy.api.config.get(f'nya_github_handler.token', None)

    def set_token(self, token=None):
        """Set access token (https://github.com/settings/tokens)"""
        self.gh = github.Github(token)
        tgpy.api.config.set(f'nya_github_handler.token', token)

    async def share_urls(self, src, recursive=True, extensions=('.py',), use_raw=False):
        """Share url of file or every file in directory (nya registry format)"""
        repo_name, branch, dir_path = self.parse_src(src)
        repo = self.gh.get_repo(repo_name)
        contents = repo.get_contents(dir_path, branch)
        if isinstance(contents, ContentFile):
            contents = [contents]
        registry = {}
        while contents:
            content = contents.pop(0)
            if content.type == "file":
                extension = os.path.splitext(content.path)[1]
                if extension in extensions:
                    try:
                        module_name = nya._Nya__parse(content.decoded_content.decode('utf-8'))[0]
                        if use_raw or module_name in ('nya_github_handler', 'nya_gitlab_handler'):
                            url = content.download_url
                        else:
                            url = content.html_url
                        registry[module_name] = url
                    except:
                        print(f"ERROR: Not a module: {content.html_url}")
            elif content.type == "dir":
                if recursive:
                    contents.extend(repo.get_contents(content.path))
        ans = '"""\n    sources:\n' + "\n".join([f'        {name}: "{registry[name]}"' for name in registry]) + '\n"""'
        await ctx.msg.respond(ans, formatting_entities=[MessageEntityCode(0, len(ans.encode('utf-16-le')) // 2)])


nya.github_handler = GithubHandler()
nya.add_source_handler(('https', 'github.com'), nya.github_handler.handler)

__all__ = []

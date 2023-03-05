"""
    name: nya_github_handler
    description: github source handler for Nya
    needs:
      nya: 0.32.6
    needs_pip:
      github: pygithub
    version: 0.0.1
"""
from urllib.parse import urlparse
import tgpy.api
import github


class GithubHandler:
    def __init__(self):
        self.gh = github.Github(self.get_token())

    async def handler(self, src):
        path = urlparse(src).path.strip('/').split('/')
        repo = path[0] + '/' + path[1]
        branch = path[3]
        file = '/'.join(path[4:])
        return self.gh.get_repo(repo).get_contents(file, branch).decoded_content.decode('utf-8')

    def get_token(self):
        return tgpy.api.config.get(f'nya_github_handler.token', None)

    def set_token(self, token=None):
        self.gh = github.Github(token)
        tgpy.api.config.set(f'nya_github_handler.token', token)


nya.github_handler = GithubHandler()
nya.add_source_handler(('https', 'github.com'), nya.github_handler.handler)

__all__ = []

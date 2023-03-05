"""
    name: nya_gitlab_handler
    description: gitlab source handler for Nya
    needs:
      nya: 0.32.6
    needs_pip:
      gitlab: python-gitlab
    version: 0.0.1
"""
from urllib.parse import urlparse
import tgpy.api
import gitlab


class GitlabHandler:
    def __init__(self):
        pass

    async def handler(self, src):
        parsed = urlparse(src)
        domain = parsed.scheme + '://' + parsed.netloc
        path = parsed.path.strip('/').split('/')
        repo = path[0] + '/' + path[1]
        branch = path[4]
        file = '/'.join(path[5:])
        gl = gitlab.Gitlab(url=domain, private_token=self.get_domain_token(domain))
        return gl.projects.get(repo).files.get(file, branch).decode().decode('utf-8')

    @staticmethod
    def stringify_domain(domain):
        domain = domain.strip('/')
        parsed = urlparse(domain)
        if not parsed.scheme:
            parsed = urlparse('https://' + domain)
        domain = parsed.scheme + '://' + parsed.netloc
        return domain.replace('.', '___')

    def get_domain_token(self, domain='https://gitlab.com'):
        domain = self.stringify_domain(domain)
        return tgpy.api.config.get(f'nya_gitlab_handler.tokens.{domain}', None)

    def set_domain_token(self, domain='https://gitlab.com', token=None):
        domain = self.stringify_domain(domain)
        tgpy.api.config.set(f'nya_gitlab_handler.tokens.{domain}', token)


nya.gitlab_handler = GitlabHandler()
nya.add_source_handler(('https', 'gitlab.com'), nya.gitlab_handler.handler)

__all__ = []

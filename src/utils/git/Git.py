import re

from git.cmd import Git
from pydantic.dataclasses import dataclass
from typing import List, Optional

@dataclass()
class GitRepository(object):
    """
    retrieve latest git tag from public git repository
    """
    repository: str
    regexp: str

    def get_all_tags(self) -> List[str]:
        g = Git()
        tags = list()
        # retrieve all tags, last element in list is the newest tag
        for r in g.ls_remote('--tags', f'https://{self.repository}').split('\n'):
            ti = r.find('refs/tags/') + len('refs/tags/')
            tags.append(r[ti:])

        return tags

    def get_latest_tag(self) -> str:
        tags = self.get_all_tags()

        r = re.compile(self.regexp)
        for t in reversed(tags):
            if r.match(t):
                return t
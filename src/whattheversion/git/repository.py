import tempfile
from typing import Optional
from git.cmd import Git
from git import Repo
from git.exc import GitCommandError
from ..utils import ApiError
from ..models import Versions, Version
from dateutil import parser
class GitRepository(object):
    origin: str
    directory: str
    repository: Repo

    def __init__(self, origin: str):
        self.origin = origin

        # initialize a temp directory for the shallow git clone
        self.directory = tempfile.mkdtemp()

        # initialize the git repository and create a partial clone
        self._git_fetch()

    def _git_fetch(self):
        """
        create a partial clone of the given git repository
        thanks to: https://stackoverflow.com/questions/65729722/git-ls-remote-tags-how-to-get-date-information
        and: https://stackoverflow.com/questions/6900328/git-command-to-show-all-lightweight-tags-creation-dates

        the fetch is required th get the timestamp for the git tags
        if timestamps wouldnt be required a remote ls would be the fastest approach

        # somethin like:
        for r in g.ls_remote('--tags', self.origin).split('\n'):
            ti = r.find('refs/tags/') + len('refs/tags/')
        :return:
        """

        try:
            self.repo = Repo.init(path=self.directory, mkdir=False)
            self.repo.create_remote(name='origin', url=self.origin)
            self.repo.git.config('extensions.partialClone', 'true')
            self.repo.git.fetch('--filter=blob:none', '--tags', '--depth=1' , 'origin')
        except GitCommandError as gce:
            raise ApiError(
                http_status=400,
                error_message=gce.stderr
            )

    def get_all_tags(self) -> Versions:
        """
        returns all tags with timestamps
        :return:
        """

        versions = Versions(versions=[])

        for t in self.repo.git.tag('-l', '--sort=-creatordate', '--format=%(creatordate:iso-local);%(refname:short)').split('\n'):
            if not t:
                continue

            ts = t.split(';')
            version = ts[1]
            timestamp = parser.parse(ts[0])

            versions.versions.append(Version(version=version, timestamp=timestamp))

        return versions

    def quick_debug_function(self):
        return

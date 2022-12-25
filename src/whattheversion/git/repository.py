import tempfile
from typing import Optional
from git.cmd import Git
from git import Repo
from git.exc import GitCommandError
from ..utils import ApiError

class GitRepository(object):
    origin: str
    regexp: Optional[str]
    directory: str
    repository: Repo

    def __init__(self, origin: str, regexp: str = None):
        self.origin = origin
        self.regexp = regexp

        # initialize a temp directory for the shallow git clone
        self.directory = tempfile.mkdtemp()

        # initialize the git repository and create a partial clone
        self._git_fetch()

    def _git_fetch(self):
        """
        create a partial clone of the given git repository
        thanks to: https://stackoverflow.com/questions/65729722/git-ls-remote-tags-how-to-get-date-information
        and: https://stackoverflow.com/questions/6900328/git-command-to-show-all-lightweight-tags-creation-dates
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

    def quick_debug_function(self):
        return self.repo.git.tag('-l', '--sort=-creatordate', '--format=\'%(creatordate:iso-strict);%(refname:short)\'')

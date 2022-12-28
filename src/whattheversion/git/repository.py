import tempfile
from git import Repo
from git.cmd import Git
from git.exc import GitCommandError
from ..utils import ApiError
from ..models import GitTag, GitTags
from dateutil import parser
from typing import List
import logging
class GitRepository(object):
    origin: str
    directory: str
    repo: Repo

    def __init__(self, origin: str):
        self.origin = origin

    # get_remote_tags isnt used anymore as the updating of dynamodb is now outsourced to
    # dedicated lambdas which can run for 15 minutes and are only triggered on a schedule,
    # so no need to verify the available tags before doing a more "expensive" git clone.
    def get_remote_tags(self) -> List[str]:
        """
        returns a list of tags found with ls-remote
        the list is used to check the dynamodb entry for the git repository
        for missing tags
        :return:
        """

        g = Git()
        tags = list()
        try:
            for r in g.ls_remote('--tags', self.origin).split('\n'):
                ti = r.find('refs/tags/') + len('refs/tags/')
                tags.append(r[ti:])
        except GitCommandError as gce:
            raise ApiError(
                http_status=400,
                error_message=gce.stderr
            )

        return tags
    def git_clone(self):
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

            logging.debug('create temp dir')
            self.directory = tempfile.mkdtemp()
            logging.debug(f'temp dir: {self.directory}')
            logging.debug('initialize git repo')
            self.repo = Repo.init(path=self.directory, mkdir=False)
            logging.debug(f'setup git origin {self.origin}')
            self.repo.create_remote(name='origin', url=self.origin)
            logging.debug(f'configure partialclone')
            self.repo.git.config('extensions.partialClone', 'true')
            logging.debug(f'git fetch')
            self.repo.git.fetch('--filter=blob:none', '--tags', '--depth=1' , 'origin')
        except GitCommandError as gce:
            logging.error(gce.stderr)
            raise ApiError(
                http_status=400,
                error_message=gce.stderr
            )

    def get_all_tags(self) -> GitTags:
        """
        returns all tags with timestamps
        :return:
        """

        t = GitTags(tags=[])

        for tag in self.repo.git.tag('-l', '--sort=-creatordate', '--format=%(creatordate:iso-local);%(refname:short)').split('\n'):
            if not tag:
                continue

            ts = tag.split(';')
            version = ts[1]
            timestamp = parser.parse(ts[0])

            t.tags.append(GitTag(tag=version, timestamp=timestamp))

        return t

    def quick_debug_function(self):
        return

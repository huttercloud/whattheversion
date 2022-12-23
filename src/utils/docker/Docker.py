from pydantic.dataclasses import dataclass
from typing import List, Optional, Dict
import requests
import re
from datetime import datetime

@dataclass()
class DockerRepository(object):
    """
    retrieve latest docker tag from docker repository
    """
    repository: str
    regexp: Optional[str] = None

    def get_registry_from_repository(self) -> str:
        """
        returns the registry name from the given repository url
        :return:
        """
        return self.repository.split('/')[0]

    def get_repository_name_from_repository(self) -> str:
        """
        return the repository name from the given repository url
        :return:
        """

        return '/'.join(self.repository.split('/')[1:])

    def get_v2_base_url(self) -> str:
        """
        return the v2 base url for docker api calls
        :return:
        """

        return f'https://{self.get_registry_from_repository()}/v2/{self.get_repository_name_from_repository()}'

    def get_docker_hub_bearer_token(self) -> str:
        """
        returns a bearer token with pull permissions for docker hub registries
        :return:
        """

        r = requests.get(
            url=f'https://auth.docker.io/token?service=registry.docker.io&scope=repository:{self.get_repository_name_from_repository()}:pull'
        )
        r.raise_for_status()

        return r.json()['token']


    def prepare_http_headers_for_registry(self) -> Dict[str, str]:
        """

        :return:
        """

        headers = dict()
        registry = self.get_registry_from_repository()

        if registry == 'registry.hub.docker.com':
            headers['Authorization'] = f'Bearer {self.get_docker_hub_bearer_token()}'

        return headers

    def get_all_tags_from_quay_io(self) -> Dict[str, datetime]:
        """
        retrieve all tags from quay and return them with their last modified date
        :return:
        """

        found_tags = []
        url=f'https://quay.io/api/v1/repository/{self.get_repository_name_from_repository()}/tag'

        while True:

        r = requests.get(url=url)
        r.raise_for_status()

        print(r.json())

    def get_all_tags_from_v2_registry(self) -> List[str]:
        """
        retrieve all docker tags from a compatible v2 registry (quay.io is not respecting pagination
        and requires its own logic!)

        :return:
        """

        found_tags = []
        url = f'{self.get_v2_base_url()}/tags/list'
        page = 1

        # return all tags
        while True:
            parameters = dict(
                # lets try to get as many tags as possible per request
                # docker hub allows more then 1000 per request
                # quay.io limits it to 50 per request
                limit=1000
            )
            # if we have tags returned, make sure request starts
            # from that tag
            try:
                parameters['last'] = found_tags[-1]
            except Exception as e:
                pass

            r = requests.get(url=url, params=parameters, headers=self.prepare_http_headers_for_registry())
            r.raise_for_status()

            # if no more tags are returned abort the loop
            if not r.json()['tags']:
                break

            found_tags += r.json()['tags']

        if self.regexp:
            r = re.compile(self.regexp)
            found_tags = list(filter(r.match, found_tags))

        return found_tags

    def get_v2_manifest_digest(self, tag: str) -> str:
        """
        get the digest from the given tag

        :param tag:
        :return:
        """

        url = f'{self.get_v2_base_url()}/manifests/{tag}'
        headers = self.prepare_http_headers_for_registry()
        headers['Accept'] = 'application/vnd.docker.distribution.manifest.v2+json'
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()

        return r.json()['config']['digest']

    def get_v2_blob_creation_date(self, digest: str) -> datetime:
        """
        get the creation timestamp from the image blob
        thanks to: https://stackoverflow.com/questions/32605556/how-to-find-the-creation-date-of-an-image-in-a-private-docker-registry-api-v2
        :param digest:
        :return:
        """

        url = f'{self.get_v2_base_url()}/blobs/{digest}'
        r = requests.get(url=url, headers=self.prepare_http_headers_for_registry())
        r.raise_for_status()

        return datetime.strptime(r.json()['created'][:-4], '%Y-%m-%dT%H:%M:%S.%f')

    def get_all_tags(self) -> List[str]:
        """
        retrieve tags with their timestmaps, sort them by timestamp
        and return sorted list of tags
        :return:
        """
        tags_with_timestamps = dict()
        if self.get_registry_from_repository() == 'quay.io':
            tags = self.get_all_tags_from_quay_io()
        else:
            # run tag retrieval for v2 registry
            tags = self.get_all_tags_from_v2_registry()

            # the tags aren't sorted by creation date
            # to sort them we need to retrieve the manifest of each tag and
            # get it's creation date
            tags_with_timestamps = dict()
            for t in tags:
                digest = self.get_v2_manifest_digest(tag=t)
                ts = self.get_v2_blob_creation_date(digest=digest)
                print(f'{t} - {digest} - {ts}')
                tags_with_timestamps[t] = ts

        return [a[0] for a in sorted(tags_with_timestamps.items(), key=lambda i: i[1])]



    def get_latest_tag(self) -> str:
            tags = self.get_all_tags()
            return tags[-1]

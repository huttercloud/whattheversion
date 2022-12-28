from typing import Dict, List
import requests
from ..models import DockerImageTag
from datetime import datetime
import logging

from ..models import DockerImageTags

class DockerRepositoryV2(object):
    repository: str
    repository_base_url: str
    http_headers: Dict
    tags: List[DockerImageTag]

    def __init__(self, repository: str, registry_base_url: str, http_headers=None):
        """
        initialize the given repository
        :param repository:
        :param http_headers:
        """
        self.repository = repository
        if http_headers is None:
            http_headers = {
                'Accept': 'application/json',
            }

        self.repository_base_url = f'{registry_base_url}/{self.repository}'
        self.http_headers = http_headers

        #self.tags = self._get_tags_with_metadata()

    def get_repository_tags(self) -> DockerImageTags:
        """
        returns all tags found for the repository
        :return:
        """

        found_tags = []
        last_tags = []

        while True:
            parameters = dict(
                # lets try to get as many tags as possible per request
                # docker hub allows more then 1000 per request
                n=10000
            )
            # if we have tags returned, make sure request starts
            # from that tag
            try:
                # quay.io and google dont care about pagination...
                parameters['last'] = found_tags[-1]
            except Exception as e:
                pass

            r = requests.get(url=f'{self.repository_base_url}/tags/list', params=parameters, headers=self.http_headers)
            r.raise_for_status()

            # if no more tags are returned abort the loop
            # also abort the loop if the returned tags are the same
            # as the last returned tags (e.g. if pagination is ignored by the registry
            if not r.json()['tags'] or r.json()['tags'] == last_tags:
                break

            last_tags = r.json()['tags']
            found_tags += r.json()['tags']

        docker_image_tags = DockerImageTags(tags=[])
        for tag in found_tags:
            # fake the timestamp just to allow for main lambda function to continue
            docker_image_tags.tags.append(DockerImageTag(tag=tag, created=datetime.now()))

        return docker_image_tags

    def get_digests_for_tags(self, tag_list: DockerImageTags) -> DockerImageTags:
        """
        retrieve the digest from the specified tags
        :param tag_list:
        :return:
        """
        docker_image_tags_with_digest = DockerImageTags(tags=[])
        for tag in tag_list.tags:
            try:
                r = requests.get(url=f'{self.repository_base_url}/manifests/{tag.tag}',
                                 headers={
                                     **self.http_headers,
                                     **{'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
                                 }
                                 )
                r.raise_for_status()

                docker_image_tags_with_digest.tags.append(
                    DockerImageTag(
                        tag=tag.tag,
                        digest=r.json()['config']['digest']
                    )
                )
            except Exception as ex:
                logging.warning(ex)

        return docker_image_tags_with_digest

    def get_timestamp_for_tags(self, tag_list: DockerImageTags) -> DockerImageTags:
        """
        retrieve the created timestamp for the given tags digest
        :param tag_list:
        :return:
        """

        docker_image_tags_with_timestamp = DockerImageTags(tags=[])
        for tag in tag_list.tags:
            try:
                r = requests.get(url=f'{self.repository_base_url}/blobs/{tag.digest}',
                                 headers={
                                     **self.http_headers,
                                     **{'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
                                 })
                r.raise_for_status()

                docker_image_tags_with_timestamp.tags.append(
                    DockerImageTag(
                        tag=tag.tag,
                        digest=tag.digest,
                        created=datetime.strptime(r.json()["created"][0:19], '%Y-%m-%dT%H:%M:%S')

                    )
                )
            except Exception as ex:
                logging.warning(ex)

        return docker_image_tags_with_timestamp


class DockerRepositoryQuay(DockerRepositoryV2):
    def __init__(self, repository: str, registry_base_url: str, http_headers=None):
        super().__init__(repository, registry_base_url, http_headers)

        self.repository_base_url = f'https://quay.io/api/v1/repository/{self.repository}'
        print(self.repository_base_url)

    def get_repository_tags(self) -> DockerImageTags:

        found_tags = []
        page = 1
        while True:
            parameters = dict(
                limit=100,
                page=page
            )

            r = requests.get(url=f'{self.repository_base_url}/tag', params=parameters)
            r.raise_for_status()

            if r.json()['tags'] == []:
                break

            found_tags += r.json()['tags']
            page += 1

        docker_image_tags = DockerImageTags(tags=[])
        for tag in found_tags:
            docker_image_tags.tags.append(
                DockerImageTag(
                    tag=tag['name'],
                    digest=tag['manifest_digest'],
                    created=datetime.strptime(tag['last_modified'], '%a, %d %b %Y %H:%M:%S -0000')
                )
            )


        return docker_image_tags

class DockerRepositoryDockerHub(DockerRepositoryV2):
    def __init__(self, repository: str, registry_base_url: str, http_headers=None):
        super().__init__(repository, registry_base_url, http_headers)

        self.repository_base_url = f'https://hub.docker.com/v2/repositories/{self.repository}'

    def get_repository_tags(self) -> DockerImageTags:

        results = []
        page = 1
        # the hub api retrieves the newest images
        # first, as we are only interested in the latest tags
        # 500 tags should be enough
        while page <= 5:
            parameters = dict(
                page=page,
                page_size=100,
            )

            r = requests.get(url=f'{self.repository_base_url}/tags', params=parameters)
            r.raise_for_status()

            results += r.json()['results']

            if not r.json()['next']:
                break
            page += 1

        docker_image_tags = DockerImageTags(tags=[])
        for tag in results:
            docker_image_tags.tags.append(
                DockerImageTag(
                    tag=tag['name'],
                    # some tags dont have a digest?
                    digest=tag.get('images',[])[0].get('digest'),
                    created=datetime.strptime(tag['tag_last_pushed'], '%Y-%m-%dT%H:%M:%S.%fZ')
                )
            )

        return docker_image_tags

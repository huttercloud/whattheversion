from typing import Dict, List
import requests
import aiohttp
import asyncio
from ..models import DockerImageTag, Versions, Version
from datetime import datetime
import json
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
            docker_image_tags.tags.append(DockerImageTag(tag=tag))

        return docker_image_tags

    def get_digests_for_tags(self, tag_list: DockerImageTags) -> DockerImageTags:
        """
        retrieve the digest from the specified tags
        :param tags:
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

    # def convert_to_versions(self) -> Versions:
    #     """
    #     convert the list of tags to a versions list for client response
    #
    #     :return:
    #     """
    #
    #     v = Versions(versions=[])
    #     for t in self.tags:
    #         v.versions.append(Version(version=t.tag, timestamp=t.created))
    #
    #     return v

    # def _get_tags_with_metadata(self) -> List[DockerImageTag]:
    #     """
    #     return all tags with their digest and creation date
    #     :return:
    #     """
    #
    #     # get all tags (sync)
    #     # then get all digest sums (async)
    #     # and then all created timestamps from the corresponding blocks (async)
    #     tags = self._get_tags()
    #
    #     loop = asyncio.get_event_loop()
    #     tags_with_digest = loop.run_until_complete(self._get_digest_for_tags(tags=tags, loop=loop))
    #     tags_with_digest_and_timestamp = loop.run_until_complete(self._get_timestamp_for_digests(tags_with_digest=tags_with_digest, loop=loop))
    #
    #     docker_image_tags = []
    #     for t in tags_with_digest_and_timestamp:
    #         if not t:
    #             continue
    #         docker_image_tags.append(DockerImageTag(**t))
    #
    #     return docker_image_tags
    #
    # async def _get_digest_for_tag(self, session: aiohttp.ClientSession, tag: str) -> Dict[str, str]:
    #     async with session.get(f'{self.repository_base_url}/manifests/{tag}') as r:
    #         try:
    #             response = await r.json()
    #             r.raise_for_status()
    #             return dict(tag=tag, digest=response['config']['digest'])
    #         except Exception as ex:
    #             logging.warning(ex)
    #             return dict()
    #
    # async def _get_digest_for_tags(self, tags: List[str], loop) -> List[Dict[str, str]]:
    #     """
    #     retrieve digest and digest creation date with aiohttp to speed up the process
    #
    #     :param tags:
    #     :return:
    #     """
    #
    #     session_digest = aiohttp.ClientSession(
    #         loop=loop,
    #         headers={
    #             **self.http_headers,
    #             **{'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    #         },
    #         connector = aiohttp.TCPConnector(
    #             limit_per_host=50
    #         )
    #     )
    #
    #     tags_with_digest = await asyncio.wait([loop.create_task(self._get_digest_for_tag(session=session_digest, tag=t)) for t in tags])
    #     await session_digest.close()
    #
    #     results = []
    #     for r in tags_with_digest[0]:
    #         re = r.result()
    #         results.append(re)
    #
    #     return results
    #
    # async def _get_timestamp_for_digest(self, session: aiohttp.ClientSession, tag: str, digest: str):
    #     async with session.get(f'{self.repository_base_url}/blobs/{digest}') as r:
    #         try:
    #             # application/octet-stream and not json is received from endpoint, no .json() for this part
    #             response = await r.text()
    #             r.raise_for_status()
    #             created = datetime.strptime(json.loads(response)["created"][0:19], '%Y-%m-%dT%H:%M:%S')
    #             return dict(tag=tag, digest=digest, created=created)
    #         except Exception as ex:
    #             logging.warning(ex)
    #             return None
    #
    # async def _get_timestamp_for_digests(self, tags_with_digest: List[Dict[str, str]], loop) -> List[Dict[str, str]]:
    #     """
    #     loop troough tags with digests and get the corresponding blobs created timestamp
    #
    #     :param tags_with_digest:
    #     :param loop:
    #     :return:
    #     """
    #
    #     session_blob = aiohttp.ClientSession(
    #         loop=loop,
    #         headers=self.http_headers,
    #         requote_redirect_url=True,
    #         connector=aiohttp.TCPConnector(
    #             limit_per_host=50
    #         )
    #     )
    #
    #     tags_with_digest_and_timestamp = await asyncio.wait([loop.create_task(self._get_timestamp_for_digest(session=session_blob, tag=t['tag'], digest=t['digest'])) for t in tags_with_digest])
    #     await session_blob.close()
    #
    #     results = []
    #     for r in tags_with_digest_and_timestamp[0]:
    #         re = r.result()
    #         results.append(re)
    #
    #     return results
    #


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

#!/usr/bin/env python3

"""
    lambda function handler for docker-api requests
"""

#
# import logging
# from whattheversion.utils import ApiError, respond, parse_docker_api_event, setup_logging
# from whattheversion.docker import create_docker_registry, DockerRepositoryQuay, DockerRepositoryV2, DockerRepositoryDockerHub
# from whattheversion.models import DockerResponse, DockerImageTags, DockerImageTag, DynamoDbEntry, compare_versions
# from whattheversion.dynamodb import DynamoDbClient
# from typing import List


import logging
from whattheversion.utils import setup_logging
from whattheversion.utils import parse_docker_eventbridge_event
from whattheversion.docker import create_docker_registry, DockerRepositoryQuay, DockerRepositoryV2, DockerRepositoryDockerHub
from whattheversion.dynamodb import DynamoDbClient
from whattheversion.models import DynamoDbEntry, DockerImageTags, DockerImageTag

from typing import List

def _remove_stored_tags(dynamodb_entry: DynamoDbEntry, repository_tags: DockerImageTags) -> List[str]:
    """
    compare docker tags found in dynamodb with tags found the docker repository
    remove all the tags already avaiable in dynamidb and return the remaining tags to
    get from the repository
    :param dynamodb_entry:
    :param repository_tags:
    :return:
    """

    # if no entry is found in dynamodb all tags need retrieval
    if not dynamodb_entry:
        return [v.tag for v in repository_tags.tags]

    stored_tags = [v.version for v in dynamodb_entry.versions.versions]
    remaining_tags = [v.tag for v in repository_tags.tags]
    remaining_tags = [v for v in remaining_tags + stored_tags if v not in stored_tags]

    return remaining_tags


setup_logging()
def handler(event, context):

    setup_logging()
    db = DynamoDbClient()
    docker_event = parse_docker_eventbridge_event(event)
    docker_registry = create_docker_registry(registry=docker_event.registry)
    docker_repository = docker_registry.get_repository(repository=docker_event.repository)
    repository_tags = docker_repository.get_repository_tags()

    # depending on the repository type the tags are collected
    # either via custom api (quay.io / docker hub) or via the registry v2 api
    if isinstance(docker_repository, DockerRepositoryQuay):
        db.upsert_docker_entry(registry=docker_registry.registry,
                               repository=docker_repository.repository,
                               tags=repository_tags)
    if isinstance(docker_repository, DockerRepositoryDockerHub):
        db.upsert_docker_entry(registry=docker_registry.registry,
                               repository=docker_repository.repository,
                               tags=repository_tags)
    elif isinstance(docker_repository, DockerRepositoryV2):
        # the operation for v2 registries is a little more involved,
        # to keep the api queries and lambda runtime to a minimum only
        # tags which arent already stored in dynamodb are queried.

        # get the dynamodb entry
        dynamodb_entry = db.get_docker_entry(registry=docker_registry.registry, repository=docker_repository.repository)

        # remove all entries which are already in the dynamodb table
        remaining_tags = _remove_stored_tags(
            dynamodb_entry=dynamodb_entry,
            repository_tags=repository_tags
        )

        # run trough the remaining entries in small batches as the lambda will
        # run into a timeout with bigger repos
        batch_size = 50
        for i in range(0, len(remaining_tags), batch_size):
            tags_batch = DockerImageTags(tags=[DockerImageTag(tag=t) for t in remaining_tags[i:i + batch_size]])
            tags_batch = docker_repository.get_digests_for_tags(tag_list=tags_batch)
            tags_batch = docker_repository.get_timestamp_for_tags(tag_list=tags_batch)

            db.upsert_docker_entry(registry=docker_registry.registry,
                                   repository=docker_repository.repository,
                                   tags=tags_batch)



if __name__ == '__main__':
    event = dict(
        detail=dict(
            # # dockerhub examples
            # repository='linuxserver/sabnzbd',
            # regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$'
            repository='filebrowser/filebrowser',
            # regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',

            # k8s.gcr.io example
            # registry='k8s.gcr.io',
            # repository='external-dns/external-dns',
            # regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$'
            #
            # # quay.io example
            # registry='quay.io',
            # repository='oauth2-proxy/oauth2-proxy',
            # regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$'
        )
    )
    handler(event, {})

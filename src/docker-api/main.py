
#!/usr/bin/env python3

"""
    lambda function handler for docker-api requests
"""


from whattheversion.utils import ApiError, respond, parse_docker_event, setup_logging
from whattheversion.docker import create_docker_registry, DockerRepositoryQuay, DockerRepositoryV2
from whattheversion.models import DockerResponse, DockerImageTags, DockerImageTag, DynamoDbEntry
from whattheversion.dynamodb import DynamoDbClient
from typing import List


def _remove_stored_tags(dynamodb_entry: DynamoDbEntry, repository_tags: DockerImageTags) -> List[str]:
    """
    compare docker tags found in dynamodb with tags found the docker repository
    remove all the tags already avaiable in dynamidb and return the remaining tags to
    get from the repository
    :param dynamodb_entry:
    :param found_tags:
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

    try:
        db = DynamoDbClient()
        docker_event = parse_docker_event(event)
        docker_registry = create_docker_registry(registry=docker_event.registry)
        docker_repository = docker_registry.get_repository(image=docker_event.image)
        dynamodb_entry = db.get_docker_entry(registry=docker_registry.registry, repository=docker_repository.repository)

        repository_tags = docker_repository.get_repository_tags()

        if not dynamodb_entry or len(dynamodb_entry.versions.versions) != len(repository_tags.tags):

            # quay.io works a little bit different then a v2 registry as there is a
            # custom public api to query to get tags with timestamps
            # the returned tags from a quay repo already contains all the required info
            if isinstance(docker_repository, DockerRepositoryQuay):
                db.upsert_docker_entry(registry=docker_registry.registry,
                                       repository=docker_repository.repository,
                                       tags=repository_tags)
            elif isinstance(docker_repository, DockerRepositoryV2):
                # remove all entries which are already in the dynamodb table
                remaining_tags = _remove_stored_tags(
                    dynamodb_entry=dynamodb_entry,
                    repository_tags=repository_tags
                )

                # run trough the remaining entries in small batches as the lambda will
                # run into a timeout with bigger repos
                for i in range(0, len(remaining_tags), 10):
                    tags_batch = DockerImageTags(tags=[DockerImageTag(tag=t) for t in remaining_tags[i:i + 10]])
                    tags_batch = docker_repository.get_digests_for_tags(tag_list=tags_batch)
                    tags_batch = docker_repository.get_timestamp_for_tags(tag_list=tags_batch)

                    db.upsert_docker_entry(registry=docker_registry.registry,
                                           repository=docker_repository.repository,
                                           tags=tags_batch)


            dynamodb_entry = db.get_docker_entry(registry=docker_registry.registry,
                                                 repository=docker_repository.repository)

        latest_version = dynamodb_entry.versions.get_latest_version(regexp=docker_event.regexp)

        response = DockerResponse(
            registry=docker_registry.registry,
            version=latest_version.version,
            timestamp=latest_version.timestamp,
            image=docker_repository.repository,
            digest=latest_version.digest,
        )

        return respond(body=response.json())

    except ApiError as ae:
        return respond(
            body=ae.return_error_response(request_id=context.aws_request_id),
            status_code=ae.httpStatus
        )


if __name__ == '__main__':
    import json
    from whattheversion.utils import FakeAwsContext
    event = dict(
        body=json.dumps(dict(
            # # dockerhub examples
            #image='linuxserver/sabnzbd',
            #regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$'
            image='filebrowser/filebrowser',
            regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',

            # k8s.gcr.io example
            # registry='k8s.gcr.io',
            # image='external-dns/external-dns',
            # regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$'
            #
            # # quay.io example
            # registry='quay.io',
            # image='oauth2-proxy/oauth2-proxy',
            # regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$'
        ))
    )
    print(handler(event, FakeAwsContext()))




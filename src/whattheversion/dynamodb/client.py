import boto3
from typing import Any, Dict, List
from botocore.exceptions import ClientError
from ..utils import ApiError, is_local_dev
import logging
import socket
from urllib.parse import urlparse
from boto3.dynamodb.conditions import Key
from ..models import GitTags, Versions, Version, DynamoDbEntry, HelmChart, DockerImageTags


class DynamoDbClient(object):
    table_name: str
    table: Any  # dynamodb.Table

    def __init__(self, table_name: str = 'whattheversion'):
        self.table_name = table_name

        try:
            resource = None
            if is_local_dev():

                hostname = 'host.docker.internal'
                try:
                    socket.gethostbyname(hostname)
                    hostname = f'http://{hostname}:8000'
                except:
                    logging.warning('Local dev instance cant resolve host.docker.internal, fallback to localhost')
                    hostname='http://localhost:8000'

                resource = boto3.resource('dynamodb',
                                          endpoint_url=hostname,
                                          region_name='eu-central-1',
                                          aws_access_key_id='local',
                                          aws_secret_access_key='local',
                                          )
            else:
                resource = boto3.resource('dynamodb')

            table = resource.Table(self.table_name)
            # check the table exists by running load()
            table.load()
            self.table = table
        except ClientError as ce:
            raise ApiError(
                http_status=500,
                error_message=ce.response['Error']['Message']
            )

    def _convert_versions_to_item_dict(self, versions: List[Version]) -> List[Dict[str, str]]:
        """
        convert the versions model to a usable dict for dynamodb insert/update
        :param versions:
        :return:
        """

        versions_to_upsert = []
        for version in versions:
            v = version.dict(exclude_unset=True, exclude_none=True)
            v['timestamp'] = v['timestamp'].isoformat()
            versions_to_upsert.append(v)

        return versions_to_upsert

    def _get_entry(self, pk: str) -> DynamoDbEntry:
        """
        searches for the given primary key and returns the found item
        :param pk:
        :return:
        """

        response = self.table.query(
            KeyConditionExpression=Key('PK').eq(pk)
        )

        i = response['Items']

        if len(i) == 0:
            return None
        if len(i) > 1:
            raise ApiError(
                error_message='Invalid table data received',
                http_status=500
            )

        entry = i[0]
        # fake versions (the versions model requires versions: List[version]
        # while the answer returns just List[versions]
        entry['versions'] = Versions(versions=entry.get('versions', []))

        return DynamoDbEntry(**entry)

    def _upsert_entry(self, pk: str, versions: Versions, payload=None, limit_version_to: int = 500):
        """
        create or update the given entry
        update operation only updates the versions list of the entry
        :param pk:
        :param payload:
        :param versions:
        :return:
        """

        if payload is None:
            payload = {}

        # if the entry exists the versions need to be updated but limited
        # to the max amount of items specifioed
        current_entry = self._get_entry(pk=pk)
        current_versions = []
        if current_entry:
            current_versions = current_entry.versions.get_versions_sorted_by_timestamp()
        given_versions = versions.get_versions_sorted_by_timestamp()
        missing_versions = [v for v in given_versions if v not in current_versions]
        # setup a new versions object to allow sorting by timestamp
        versions_to_insert = Versions(
            versions=missing_versions + current_versions
        ).get_versions_sorted_by_timestamp()[:limit_version_to]

        # create/update entry if it doesnt exist
        try:
            item = {
                **dict(
                    PK=pk,
                    versions=self._convert_versions_to_item_dict(versions_to_insert)
                ),
                **payload
            }
            self.table.put_item(
                Item=item,
                #ConditionExpression=Attr('PK').not_exists(),
                ReturnValues='NONE',
            )
            return
        except ClientError as ce:
            if ce.response['Error']['Code'] == 'ConditionalCheckFailedException':
                pass
            else:
                raise ApiError(
                    http_status=500,
                    error_message=ce.response['Error']['Message']
                )

    def _get_git_pk(self, origin: str) -> str:
        """
        returns the primary key for a git entry
        :param origin:
        :return:
        """

        # parse the given origin http(s) url
        up = urlparse(origin)
        git_host = up.netloc
        git_repo = up.path[1:]

        # remove trailiing .git
        if git_repo.endswith('.git'):
            git_repo = git_repo[:-4]

        return f'GIT#{git_host}#{git_repo}'

    def get_git_entry(self, origin: str) -> DynamoDbEntry:
        """
        retrieves the dynamodb entry for the git repo
        :param origin:
        :return:
        """

        g = self._get_entry(pk=self._get_git_pk(origin=origin))

        return g

    def upsert_git_entry(self, origin, tags: GitTags):
        """
        create or update the given git entry
        :param tags:
        :param origin:
        :return:
        """

        self._upsert_entry(
            pk=self._get_git_pk(origin=origin),
            versions=tags.convert_to_versions()
        )

    def _get_helm_pk(self, registry: str, chart_name: str) -> str:
        """
        returns the primary key for a helm entry
        :param origin:
        :return:
        """

        up = urlparse(registry)
        registry_host = up.netloc
        registry_path = up.path

        return f'HELM#{registry_host}{registry_path}#{chart_name}'

    def get_helm_entry(self, registry: str, chart_name: str) -> DynamoDbEntry:
        """
        retrieves the dynamodb entry for the helm repo/chart
        :param origin:
        :return:
        """

        h = self._get_entry(pk=self._get_helm_pk(registry=registry, chart_name=chart_name))

        return h

    def upsert_helm_entry(self, registry: str, chart: HelmChart):
        """
        create or update the given git entry
        :param tags:
        :param origin:
        :return:
        """

        self._upsert_entry(
            pk=self._get_helm_pk(registry=registry, chart_name=chart.name),
            versions=chart.convert_to_versions()
        )

    def _get_docker_pk(self, registry: str, repository: str) -> str:
        """
        returns the primary key for a docker entry
        :param origin:
        :return:
        """

        return f'DOCKER#{registry}#{repository}'

    def get_docker_entry(self, registry: str, repository: str) -> DynamoDbEntry:
        """
        retrieves the dynamodb entry for the helm repo/chart
        :param origin:
        :return:
        """

        d = self._get_entry(pk=self._get_docker_pk(registry=registry, repository=repository))

        return d

    def upsert_docker_entry(self, registry: str, repository: str, tags: DockerImageTags):
        """
        create or update the given git entry
        :param tags:
        :return:
        """

        self._upsert_entry(
            pk=self._get_docker_pk(registry=registry, repository=repository),
            versions=tags.convert_to_versions()
        )

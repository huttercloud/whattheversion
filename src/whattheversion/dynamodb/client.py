import boto3
from typing import Any, Dict
from botocore.exceptions import ClientError
from ..utils import ApiError, is_local_dev
import logging
import socket
from urllib.parse import urlparse
from boto3.dynamodb.conditions import Key, Attr
from ..models import GitTags, Versions, DynamoDbEntry

class DynamoDbClient(object):

    table_name: str
    table: Any # dynamodb.Table

    def __init__(self, table_name: str = 'whattheversion'):
        self.table_name = table_name

        try:
            resource = None
            if is_local_dev():
                try:
                    socket.gethostbyname('host.docker.internal')
                    resource = boto3.resource('dynamodb', endpoint_url="http://host.docker.internal:8000")
                except:
                    logging.warning('Local dev instance cant resolve host.docker.internal, fallback to localhost')
                    resource = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
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
        entry['versions'] = Versions(versions=entry['versions'])

        return DynamoDbEntry(**entry)

    def _upsert_entry(self, pk: str, versions: Versions, payload=None):
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

        # create entry if it doesnt exist
        try:
            item={**dict(
                    PK=pk,
                    versions=[dict(version=v.version, timestamp=v.timestamp.isoformat()) for v in versions.get_versions_sorted_by_timestamp()]
                ),
                **payload
            }
            self.table.put_item(
                Item=item,
                ConditionExpression=Attr('PK').not_exists(),
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

        # there is surely a more efficient and neater way to
        # only insert the missing dicts into the versions field
        # but good enough for now...
        current_entry = self._get_entry(pk=pk)
        versions_missing = [v for v in current_entry.versions.get_versions_sorted_by_timestamp() + versions.get_versions_sorted_by_timestamp() if v not in current_entry.versions.get_versions_sorted_by_timestamp()]

        if versions_missing:
            # update loop for versions
            try:
                self.table.update_item(
                    Key={
                        'PK': pk,
                    },
                    UpdateExpression='SET #v = list_append(#v, :versions)',
                    ExpressionAttributeNames={
                        '#v': 'versions',
                    },
                    ExpressionAttributeValues={
                        ':versions': [dict(version=v.version, timestamp=v.timestamp.isoformat()) for v in versions_missing]
                    },
                    ConditionExpression=Attr('PK').exists()

                )
                return
            except ClientError as ce:
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

        return f'GIT#{git_host}#{git_repo}'


    def get_git_entry(self, origin: str) -> DynamoDbEntry:
        """
        retrieves the dynamodb entry for the git repo
        :param origin:
        :return:
        """

        g = self._get_entry(pk=self._get_git_pk(origin=origin))

        return g


    def upsert_git_entry(self, origin, tags = GitTags):
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


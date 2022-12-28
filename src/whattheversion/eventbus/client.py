import boto3
from typing import Any

from ..models import UpsertDynamoDBEvent, UpsertGitEventDetail

class EventBusClient(object):
    client: Any

    def __init__(self):
        self.client = boto3.client('events')


    def put_git_event(self, repository: str):
        """
        creates a custom git event in eventbridge
        :param repository:
        :return:
        """

        event = UpsertDynamoDBEvent().dict()

        event['Detail'] = UpsertGitEventDetail(
            repository=repository
        ).json()

        self.client.put_events(
            Entries=[
                event
            ]
        )

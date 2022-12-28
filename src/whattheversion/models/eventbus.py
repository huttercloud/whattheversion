from pydantic import BaseModel, Json
from typing import Any, Optional



class UpsertDynamoDBEvent(BaseModel):
    Source: str = 'cloud.hutter.whattheversion'
    DetailType: str = 'Create or Update DynamoDB versions entry'
    Detail: Json[Any]

class UpsertGitEventDetail(BaseModel):
    source: str = 'git'
    repository: str

class UpsertDockerEventDetail(BaseModel):
    source: str = 'docker'
    registry: str
    image: str

class UpsertHelmEventDetail(BaseModel):
    source: str = 'helm'
    registry: str
    chart: str



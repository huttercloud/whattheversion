from pydantic import BaseModel, Json, AnyHttpUrl
from typing import Any



class UpsertDynamoDBEvent(BaseModel):
    Source: str = 'cloud.hutter.whattheversion'
    DetailType: str = 'Create or Update DynamoDB versions entry'
    Detail: Json[Any]

class UpsertGitEventDetail(BaseModel):
    source: str = 'git'
    repository: AnyHttpUrl

class UpsertDockerEventDetail(BaseModel):
    source: str = 'docker'
    registry: str
    repository: str

class UpsertHelmEventDetail(BaseModel):
    source: str = 'helm'
    registry: AnyHttpUrl
    chart: str



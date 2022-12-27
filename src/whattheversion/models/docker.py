from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, List
from datetime import datetime
from .versions import Versions, Version

class DockerRequest(BaseModel):
    registry: str = 'registry.hub.docker.com'
    image: str
    regexp: Optional[str]

class DockerResponse(BaseModel):
    registry: str
    version: str
    timestamp: datetime
    image: str


class DockerImageTag(BaseModel):
    tag: str
    digest: str
    created: datetime

class DockerRepository(BaseModel):
    repository: str

    tags: List[DockerImageTag]


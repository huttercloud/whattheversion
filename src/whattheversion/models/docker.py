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
    digest: Optional[str]
    created: Optional[datetime]

class DockerImageTags(BaseModel):
    tags: List[DockerImageTag]


    def convert_to_versions(self) -> Versions:
        v = Versions(versions=[])

        for e in self.tags:
            v.versions.append(Version(version=e.tag, timestamp=e.created, digest=e.digest))

        return v
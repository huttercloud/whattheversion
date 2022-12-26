from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, List
from datetime import datetime
from .versions import Versions, Version

class GitRequest(BaseModel):
    repository: AnyHttpUrl
    regexp: Optional[str]

class GitResponse(BaseModel):
    repository: AnyHttpUrl
    version: str
    timestamp: datetime

class GitTag(BaseModel):
    tag: str
    timestamp: datetime

class GitTags(BaseModel):
    tags: List[GitTag]

    def convert_to_versions(self) -> Versions:

        v = Versions(versions=[])
        for t in self.tags:
            v.versions.append(Version(version=t.tag, timestamp=t.timestamp))

        return v

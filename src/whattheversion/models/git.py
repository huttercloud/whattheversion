from pydantic import BaseModel, AnyHttpUrl
from typing import Optional
from datetime import datetime

class GitRequest(BaseModel):
    repository: AnyHttpUrl
    regexp: Optional[str]

class GitResponse(BaseModel):
    repository: str
    version: str
    timestamp: datetime
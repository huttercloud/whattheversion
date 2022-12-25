from pydantic import BaseModel, AnyHttpUrl
from typing import Optional

class GitRequest(BaseModel):
    repository: AnyHttpUrl
    regexp: Optional[str]


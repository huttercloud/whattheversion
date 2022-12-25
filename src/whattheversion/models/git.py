from pydantic import BaseModel
from typing import Optional

class GitRequest(BaseModel):
    repository: str
    regexp: Optional[str]


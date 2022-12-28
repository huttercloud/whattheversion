from pydantic import BaseModel
from .versions import Versions
from typing import List, Dict, Optional

class DynamoDbEntry(BaseModel):
    PK: str
    versions: Versions

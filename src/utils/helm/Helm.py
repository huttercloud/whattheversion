from pydantic.dataclasses import dataclass
from typing import List, Optional

@dataclass()
class HelmRepository(object):
    """
    retrieve latest helm tag from helm repository
    """
    repository: str
    regexp: Optional[str] = None

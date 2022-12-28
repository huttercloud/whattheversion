import subprocess
from ..utils import is_local_dev, ApiError
import os
import json
from typing import Dict, Any


def download_and_convert_helm_index_to_json(index_url: str) -> Dict[Any, Any]:
    """
    downloads a helm index and converts it to json
    with external tooling
    :return:
    """

    result = subprocess.run(['helm-to-json', index_url], capture_output=True)
    if result.returncode > 0:
        raise ApiError(
            http_status=500,
            error_message=f'Unable to load yaml file: {result.stderr}'
        )

    try:
        parsed = json.loads(result.stdout)
        return parsed
    except json.JSONDecodeError as je:
        raise ApiError(
            http_status=500,
            error_message=f'Unable to parse yaml file: {je.msg}'
        )

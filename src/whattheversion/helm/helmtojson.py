import subprocess
from ..utils import ApiError
import json
from typing import Dict, Any
import logging


#
# go binary isnt used anymore (didnt work in every case and with the move to event driven)
# refresh of the helm entries in dynamodb the general slowness doesnt matter anymore!
#
def download_and_convert_helm_index_to_json(index_url: str) -> Dict[Any, Any]:
    """
    downloads a helm index and converts it to json
    with external tooling
    :return:
    """

    logging.debug(f'Download helm manifest from {index_url}')
    result = subprocess.run(['helm-to-json', index_url], capture_output=True)
    if result.returncode > 0:
        logging.error(result.stderr)
        raise ApiError(
            http_status=500,
            error_message=f'Unable to load yaml file: {result.stderr}'
        )

    try:
        parsed = json.loads(result.stdout)
        return parsed
    except json.JSONDecodeError as je:
        logging.error(je.msg)
        raise ApiError(
            http_status=500,
            error_message=f'Unable to parse yaml file: {je.msg}'
        )

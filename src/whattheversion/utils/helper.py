import json
from typing import Optional, Dict, List
import aiohttp
import asyncio

class ApiError(Exception):
    """
    represents any api error
    """

    errorType: str
    httpStatus: int
    requestId: Optional[str]
    errorMessage: str

    def __init__(self, error_message: str, error_type: str = None, http_status: int = 200, request_id: str = None):
        self.errorType = error_type
        self.errorMessage = error_message
        self.requestId = request_id
        self.httpStatus = http_status

    def return_error_response(self, request_id: str):
        """
        returns a preformated error response

        example of an error response returned by the http api gateway
        {
            "errorMessage": "name 'invalidfauybfeuoibngfoi4e' is not defined",
            "errorType": "NameError",
            "requestId": "2c5f6532-7a50-4163-800d-00798dadcb54",
            "stackTrace": [
                "  File \"/var/task/main.py\", line 21, in handler\n    invalidfauybfeuoibngfoi4e\n"
            ]
        }

        :param request_id:
        :return:
        """

        error_response = dict(
            errorMessage=self.errorMessage,
            errorType="WHattheversion Error",
            requestId=request_id,
        )

        return json.dumps(error_response)



class FakeAwsContext(object):
    """
        fake the aws context object for local (non sam) executions of the lambdas
    """
    aws_request_id: str

    def __init__(self):
        self.aws_request_id = 'local'



def respond(body: str, status_code: int = 200, is_base64_encoded: bool = False, headers: Dict[str, str] = None,
            cookies: List[str] = None):
    """
    send response to the api gateway
    :param body:
    :param status_code:
    :param is_base64_encoded:
    :param headers:
    :param cookies:
    :return:
    """

    if not headers:
        headers = {"content-type": "application/json"}

    response = dict(
        isBase64Encoded=is_base64_encoded,
        statusCode=status_code,
        body=body,
        headers=headers,
        cookies=cookies
    )

    return response

async def aget(url, session):
    """
    run an aysnc get request
    :param url:
    :param session:
    :return:
    """
    async with session.get(url) as response:
        return await response.read()
#
# def aget(url: str, headers: Dict = {}, r: int = 3):
#     """
#      run an aysnc get request
#     :param url:
#     :param headers:
#     :param r:
#     :return:
#     """
#
#     async with aiohttp.ClientSession(headers=headers) as session:
#     for i in range(r):
#         task = asyncio.ensure_future(_aget(url=',session=session))
#         tasks.append(task)
#     responses = await asyncio.gather(*tasks)
#
#     print(responses)
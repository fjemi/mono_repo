from requests import post
from requests.structures import CaseInsensitiveDict
from typing import Optional, Dict, Union
from json import dumps
from box import Box
from dataclasses import dataclass


@dataclass
class Data:
    url: str = 'http://192.168.12.1//TMI/v1/network/configuration?set=ap'
    token: str = None
    device_configs: Union[Box, Dict] = None


def set_device_configs(data: Data) -> Optional[Box]:
    '''
    https://reqbin.com/req/python/5k564bhv/get-request-bearer-token-authorization-header-example
    
    curl -H "Content-Type: application/json" --data @"data/device_config.json" http://192.168.12.1//TMI/v1/network/configuration\?set\=ap -H'Authorization: Bearer [TOKEN]'
    '''

    # Set request headers
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = 'application/json'
    headers["Authorization"] = f'Bearer {data.token}'

    # Make the request
    response = post(
        url=data.url,
        headers=headers,
        data=data.device_configs,
        timeout=(5, 25), )

    if response.status_code == 200:
        return Box(response.json())
    
    return None


def main() -> None:
    from json import dump, load
    from get_device_token import get_device_token

    
    token = get_device_token()
    with open('data/device_configs.json', 'r') as file:
        device_configs = load(file)
    
    data = Data(token=token, device_configs=device_configs)
    result = set_device_configs(data)
    print(result)


if __name__ == '__main__':
    main()

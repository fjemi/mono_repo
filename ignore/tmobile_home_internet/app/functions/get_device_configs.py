from requests import get
from requests.structures import CaseInsensitiveDict
from typing import Optional
from box import Box
from dataclasses import dataclass


@dataclass
class Data:
    token: str = None
    url: str = 'http://192.168.12.1//TMI/v1/network/configuration?get=ap'


def get_headers(token: str) -> CaseInsensitiveDict:
    # Set request headers
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = 'application/json'
    headers["Authorization"] = f'Bearer {token}'
    return headers


def get_device_configs(data: Data) -> Optional[Box]:
    '''
    https://reqbin.com/req/python/5k564bhv/get-request-bearer-token-authorization-header-example
    
    curl -H "Content-Type: application/json" --data @"data/device_config.json" http://192.168.12.1//TMI/v1/network/configuration\?set\=ap -H'Authorization: Bearer <TOKEN>'
    '''

    # Make the request
    response = get(url=data.url, headers=get_headers(data.token))
    if response.status_code == 200:
        return Box(response.json())
    
    return None


def main() -> None:
    from json import dump
    from get_device_token import get_device_token

    data = Data(token=get_device_token())
    device_configs = {'device_configs': get_device_configs(data=data)}
    
    with open('data/device_configs.json', 'w', encoding='utf-8') as file:
        dump(device_configs, file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()

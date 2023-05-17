from requests import get
from json import loads
from typing import Optional
from box import Box
from dataclasses import dataclass


@dataclass
class Data:
    url: str = 'http://192.168.12.1/TMI/v1/gateway?get=all'


def get_device_info(data: Data) -> Optional[Box]:
    '''
    Get the configurations for the 5G gateway
    '''
    response = get(url=data.url)
    if response.status_code == 200:
        return Box(response.json())
        
    return None


def main() -> None:
    from json import dump

    data = Data()
    device_info = {'device_info': get_device_info(data)}
    with open(
        'data/device_info.json',
        'w',
        encoding='utf-8', ) as file:
        dump(
            device_info,
            file,
            ensure_ascii=False,
            indent=2, )
        


if __name__ == '__main__':
    main()

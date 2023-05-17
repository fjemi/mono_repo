from requests import get, post
from os import environ
from prodict import Prodict

from get_token import get_token


ENV = Prodict(environ)
URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/'
URL = f'http://{ENV.HOST}/cgi-bin/luci/;stok=STOK/api/misystem/'


def get_device_info(token: str = get_token()) -> Prodict:
    ''''''
    url = URL.replace('STOK', token)
    response = get(url=url)
    if response.status_code == 200:
        data = Prodict(response.json())
        return data
    return None


def main() -> None:
    ''''''
    from json import dumps


    info = get_device_info()
    print(dumps(info, indent=2))


if __name__ == '__main__':
    main()
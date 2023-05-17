from requests import get, post
from dataclasses import dataclass, asdict
from os import environ
from prodict import Prodict


ENV = Prodict(environ)
URL = f'http://{ENV.HOST}/cgi-bin/luci/api/xqsystem/login'


@dataclass
class Credentials:
    username: str = ENV.USERNAME
    password: str = ENV.PASSW0RD


def get_token(credentials: Credentials = Credentials()) -> str:
    '''
    https://github.com/home-assistant/core/blob/67c35652f0d49dc56e1e934fab3b2c51f5f82592/homeassistant/components/xiaomi/device_tracker.py#L116
    '''
    data = asdict(credentials)
    response = post(
        url=URL,
        data=data,
        timeout=5,
    )
    if response.status_code == 200:
        data = Prodict(response.json())
        return data.token

    return None


def main() -> None:
    '''Example usage'''
    from json import dumps


    credentials = Credentials()
    token = get_token(credentials)
    print(dumps(token, indent=2))


if __name__ == '__main__':
    main()

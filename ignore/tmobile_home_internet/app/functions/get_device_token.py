from requests import post
from dataclasses import dataclass, asdict, field
from json import dumps
from os import getenv
from typing import Optional
from box import Box


@dataclass
class Environment:
    '''
    Environment variables used within this script
    - password: The gateway's admin password
    - username: The gateway's admin username
    - root_path: The project's root path
    '''
    username: str = field(default_factory=lambda: getenv('USERNAME'))
    password: str = field(default_factory=lambda: getenv('PASSWORD'))
    root_path: str = field(default_factory=lambda: getenv('ROOT_PATH'))


ENV = Environment()


@dataclass
class Data:
    url: str = 'http://192.168.12.1/TMI/v1/auth/login'
    username: str = ENV.username
    password: str = ENV.password


def get_device_token(data: Data = Data()) -> Optional[str]:
    '''
    Gets a token from the 5G gateway

    Parameters
    - credentials, Credentials: Credentials needed to access the gateway

    Returns
    - token, str: The gateway token
    '''
    # Request parameters
    headers = {'Content-Type': 'application/json'}
    # Dict to JSON
    credentials = {'username': data.username, 'password': data.password}
    
    # Make the request
    response = post(
        url=data.url,
        data=credentials,
        headers=headers, )

    if response.status_code != 200:
        return None

    json_response = Box(response.json())
    # Get the token
    return json_response.auth.token


def main() -> None:
    from json import dump

    token = {'token': get_device_token()}
    path = f"{ENV.root_path}/data/token.json"
    with open(
        path,
        'w',
        encoding='utf-8', ) as file:
        dump(
            token,
            file,
            ensure_ascii=False,
            indent=2, )


if __name__ == '__main__':
    main()

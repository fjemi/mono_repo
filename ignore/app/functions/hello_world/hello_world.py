#!/usr/bin/env python3

from app.shared.get_config.get_config import get_config
from json import dumps


CONFIG = get_config(__file__)


def hello_world(name: str = None, config: dict = CONFIG) -> str:
    # Set function docstring
    hello_world.__doc__ = config['docstrings']
    
    if name is None:
        return 'hello world'
    return f'hello {name}'



def main():
    print(hello_world())
    print(hello_world('earth'))
    print(hello_world.__doc__)


if __name__ == '__main__':
    main()

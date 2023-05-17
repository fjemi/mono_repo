def ping(data = None) -> str:
    '''
    Ping the API

    Parameters: None

    Returns: str
    '''
    return 'pong'


def main() -> None:
    print(ping())


if __name__ == '__main__':
    main()
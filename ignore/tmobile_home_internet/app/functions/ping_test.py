from ping import ping


def ping_test():
    '''Test that '''
    result = ping(data=None)

    assert isinstance(result, str)
    assert result == 'pong'

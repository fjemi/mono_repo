from get_device_token import get_device_token, Data, Environment
from unittest.mock import patch, Mock
from typing import Any, Optional
from box import Box


@patch('get_device_token.getenv')
def setting_credentials_test(mock_getenv: patch) -> None:
    '''Test that credentials are set from env variables'''

    # Use side effect to return specific value when function called with arg
    values = Box({
        'USERNAME': 'username',
        'PASSWORD': 'password',
        'ROOT_PATH': 'path'}, )    
    def side_effect(arg: Any) -> Optional[Any]:
        return values[arg]
    mock_getenv.side_effect = side_effect

    env = Environment()

    # Should 
    assert env.username == values.USERNAME
    assert env.password == values.PASSWORD
    assert env.root_path == values.ROOT_PATH
    

@patch('get_device_token.post')
def successful_response_test(mock_request: patch) -> None:
    '''
    Test that the token is recieved when the request response status is 200
    '''
    # Setup mock request and response
    mock_response = Mock()
    mock_response.json.return_value = {'auth': {'token': 'token'}}
    mock_response.status_code = 200
    mock_request.return_value = mock_response

    # Set arbitary credentials
    token = get_device_token(data=Data())
    expected = 'token'
    
    # Should have made the request and returned the expected result
    assert token == expected
    assert mock_request.called is True


@patch('get_device_token.post')
def failed_response_test(mock_request: patch) -> None:
    '''
    Test that None is recieved when the request status is not 200
    '''
    # Setup mock request and response
    mock_response = Mock()
    mock_response.status_code = 400
    mock_request.return_value = mock_response

    # Expected and actual results
    token = get_device_token(data=Data())
    expected = None
    
    # Should have made the request and returned the expected result
    assert token == expected
    assert mock_request.called is True


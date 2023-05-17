from get_device_configs import get_device_configs, Data, get_headers
from unittest.mock import patch, Mock
from typing import Any, Optional
from box import Box


def get_headers_test() -> None:
    '''Test that the headers for authenitcating the request are returned'''
    headers = get_headers(token='ARBITARY_TOKEN')

    assert type(headers).__name__ == 'CaseInsensitiveDict'
    assert headers == {
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer ARBITARY_TOKEN', }


@patch('get_device_configs.get')
def successful_request_test(mock_request: patch) -> None:
    '''Test the behavior for a successful request'''

    # Expected result from running the function
    expected = Box({'device_configs': {}})

    # Setup mock request and response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected
    mock_request.return_value = mock_response

    # Should return the device configs if the request is successful
    data = Data(token='ARBITARY_TOKEN', url='ARBITARY_URL')
    device_configs = get_device_configs(data)

    assert mock_request.called is True
    assert isinstance(device_configs, Box)
    assert device_configs.device_configs is not None


@patch('get_device_configs.get')
def failed_request_test(mock_request: patch) -> None:
    '''Test behavior for a failed request'''

    # Setup mock request and response
    mock_response = Mock()
    mock_response.status_code = 400
    mock_request.return_value = mock_response

    # Should return None if the request fails
    data = Data(token='ARBITARY_TOKEN', url='ARBITARY_URL')
    device_configs = get_device_configs(data)

    assert mock_request.called is True
    assert device_configs is None

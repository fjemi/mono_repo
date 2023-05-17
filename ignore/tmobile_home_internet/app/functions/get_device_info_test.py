from get_device_info import get_device_info, Data
from unittest.mock import patch, Mock
from typing import Any, Optional
from box import Box


@patch('get_device_info.get')
def successful_request_test(mock_request: patch) -> None:
    '''Test the behavior for a successful request'''

    # Expected result from running the function
    expected = Box({'device_info': {}})

    # Setup mock request and response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected
    mock_request.return_value = mock_response

    # Should return the device's info when the request is successful
    data = Data()
    device_info = get_device_info(data)

    assert mock_request.called is True
    assert isinstance(device_info, Box)
    assert device_info.device_info is not None


@patch('get_device_info.get')
def failed_request_test(mock_request: patch) -> None:
    '''Test behavior for a failed request'''

    # Setup mock request and response
    mock_response = Mock()
    mock_response.status_code = 400
    mock_request.return_value = mock_response

    # Should return None if the request fails
    data = Data()
    device_info = get_device_info(data)

    assert mock_request.called is True
    assert device_info is None

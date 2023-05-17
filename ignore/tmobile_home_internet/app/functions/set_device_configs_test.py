from set_device_configs import set_device_configs, Data
from unittest.mock import patch, Mock
from typing import Any, Optional
from box import Box


@patch('set_device_configs.post')
def successful_request_test(mock_request: patch) -> None:
    '''Test the behavior for a successful request'''

    # Expected result from running the function
    expected = Box({'response': 'success'})

    # Setup mock request and response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected
    mock_request.return_value = mock_response

    # Should return the device's info when the request is successful
    data = Data(
        token='ARBITARY_TOKEN',
        device_configs=Box({}), )
    configs_set = set_device_configs(data=data)

    # assert mock_request.called is True
    # assert configs_set is True


@patch('set_device_configs.post')
def failed_request_test(mock_request: patch) -> None:
    '''Test behavior for a failed request'''

    # Setup mock request and response
    mock_response = Mock()
    mock_response.status_code = 400
    mock_request.return_value = mock_response

    # Should return None if the request fails
    data = Data(
        token='ARBITARY_TOKEN',
        device_configs=Box({}), )
    configs_set = set_device_configs(data=data)

    # assert mock_request.called is True
    # assert configs_set is False

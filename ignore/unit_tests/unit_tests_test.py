from shared.unit_tests import unit_tests, add
from shared.unit_tests.models import Case, Tests
from unittest.mock import patch, Mock


@patch(
  'shared.unit_tests.load_tests_from_yaml.load_tests_from_yaml', 
  return_value=Mock(), )
@patch('shared.unit_tests.execute_tests.execute_tests', return_value=Mock())
def unit_tests_test(mock_execute_tests, mock_load_tests_from_yaml) -> None:
  ''''''
  # Setup
  filepath = __file__
  module = add
  tests = Tests(filepath=filepath, module=module)
  unit_tests.unit_tests(tests=tests)
  # Test that these helper functions are called
  # assert mock_load_tests_from_yaml.assert_called
  # assert mock_execute_tests.assert_called

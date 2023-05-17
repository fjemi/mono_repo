from dataclasses import dataclass
from typing import List, Any, Dict
import sys
import pytest
import yaml

from shared.get_function_to_test_from_test_function import app
from test_resources import app as test_resources


TEST_RESOURCES_DIR = __file__.replace('app.py', 'test_resources')


@dataclass
class Tests:
  test_description: str = None
  case_descriptions: List[str] | str = None
  cases: List[Any] | Any = None
  expected_results: List[Any] | Any = None
  expected_fields: List[bool] | bool = None


def test_get_test_function_name() -> None:
  tests = '''
    test_description: Should return the name of the callable that the function 
      (the function to test) is executed in.
    case_descriptions: function doesn't take in arguments
    cases:
    - data: null
    - data: null
    - data: null
    expected_results:
    - test_get_test_function_name
    - test_get_test_function_name
    - test_get_test_function_name
  '''
  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.get_test_function_name(data=_case)
    
    # Result should be the name of this test function
    assert result == tests.expected_results[i]


def test_get_function_name_from_test_function_name() -> None:
  tests = '''
    test_description: Should return the name of the callable that the function 
      (the function to test) is executed in.
    case_descriptions: 
    - test function name with a prefix
    - test function name with a prefix
    - test function name with a suffix
    - test function name with a suffix
    cases:
    - prefix: 'prefix_0_'
      test_function_name: prefix_0_test_function_name
    - prefix: 'prefix_1_'
      test_function_name: prefix_1_test_function_name
    - suffix: '_suffix_0'
      test_function_name: test_function_name_suffix_0
    - suffix: '_suffix_1'
      test_function_name: test_function_name_suffix_1
    expected_results:
    - test_function_name
    - test_function_name
    - test_function_name
    - test_function_name
  '''
  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
  tests = Tests(**tests)

  # Get function to test
  data = app.Data(
    test_function_name=app.get_test_function_name(), 
    _module=app, 
  )
  function = app.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)
    
    # Result should remove the suffix of prefix from the test function name
    # to get the name of the function being tested
    assert result == tests.expected_results[i]


def test_get_function_from_module() -> None:
  tests = '''
    test_description: Should return a function from a module
    case_descriptions: 
    - add function in test_resources.app
    - subtract function in test_resources.app
    cases:
    - _module: {test_resources}
      function_name: add
    - _module: {test_resources}
      function_name: subtract
    expected_results:
    - add
    - subtract
  '''
  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
  tests = Tests(**tests)

  # Get function to test
  data = app.Data(
    test_function_name=app.get_test_function_name(), 
    _module=app, 
  )
  function = app.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case['_module'] = test_resources

    # Execute function
    result = function(**_case)
    
    # Result should be a function with the correct name
    assert type(result).__name__ == 'function'
    assert result.__name__ == tests.expected_results[i]


def test_setup_main_data() -> None:
  tests = '''
    test_description: Should return the name of the callable that the function 
      (the function to test) is executed in.
    case_descriptions: 
    - a empty dictionary
    - a dictionary
    - a empty dataclass
    - a dataclass
    cases:
    - {}
    - test_function_name: test_function_name
      _module: _module
      prefix: prefix
      suffix: suffix
      function_name: function_name
      function: function
    - {}
    - test_function_name: test_function_name
      _module: _module
      prefix: prefix
      suffix: suffix
      function_name: function_name
      function: function
    expected_results:
    - test_function_name: null
      _module: null
      prefix: test_
      suffix: _test
      function_name: null
      function: null
    - test_function_name: test_function_name
      _module: _module
      prefix: prefix
      suffix: suffix
      function_name: function_name
      function: function
    - test_function_name: null
      _module: null
      prefix: test_
      suffix: _test
      function_name: null
      function: null
    - test_function_name: test_function_name
      _module: _module
      prefix: prefix
      suffix: suffix
      function_name: function_name
      function: function
  '''
  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
  tests = Tests(**tests)

  # Get function to test
  data = app.Data(
    test_function_name=app.get_test_function_name(), 
    _module=app, 
  )
  function = app.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    # Convert the third and fourth cases to dataclasses before processing
    if i in [2, 3]:
      _case = app.Data(**_case)
    print(_case)
    

    # Execute function
    result = function(data=_case)
    
    # Result should be of type `Data` and have the expected values
    assert type(result).__name__ == 'Data'
    for field, expected_value in tests.expected_results[i].items():
      result_value = getattr(result, field)
      assert result_value == expected_value


if __name__ == '__main__':
  # Invoke pytest for this module
  pytest_arguments = sys.argv
  pytest_arguments.extend(['-x', '-s', '--vv', '--cov', '.'])
  pytest.main()
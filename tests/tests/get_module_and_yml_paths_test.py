#! /usr/bin/env python3

import sys
import pytest
from dataclasses import dataclass
from yaml import safe_load
from typing import Any, List, Dict

from app import get_module_and_yml_paths
from app import get_module_function
from tests.get_module_and_yml_paths_resources import app as test_resources


# Path to the test resources directory
TEST_RESOURCES_DIR = __file__.replace('app_test.py', 'test_resources')


@dataclass
class Tests:
  test_description: str | None = None
  case_descriptions: List[Dict[str, str]] | Dict[str, str] | None = None
  cases: List[Any] | Any | None = None
  expected_results: List[Any] | Any | None = None


def test_get_file_extension() -> None:
  tests = '''
    test_description: Should return the extension for a file given its path
    case_descriptions:
    - File extension is `.ext`
    - File extension is `.extension`
    - File extension is `.py`
    - File extension is `.yml`
    - File extension is `.yaml`
    cases:
      - data: file.ext
      - data: file.extension
      - data: file.py
      - data: file.yml
      - data: file.yaml
    expected_results:
    - .ext
    - .extension
    - .py
    - .yml
    - .yaml
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_module_function.Data(
    test_function_name=get_module_function.get_test_function_name(), 
    _module=app,
  )
  function = get_module_function.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)
    
    # Verify that result is the correct extension
    assert result == tests.expected_results[i]


def test_case_setup_data_for_str() -> None:
  tests = '''
    test_description: Should return a `Data` objected for a string or path 
      input; the path is mapped to its corresponding field base on the file's
      extension.
    case_descriptions:
    - path with file with `.py` extension
    - path with file with `.yml` extension
    - path with file with `.yaml` extension
    cases:
    - data: path.py
    - data: path.yml
    - data: path.yaml
    expected_results:
    - py_path: path.py
      yml_path: null
    - py_path: null
      yml_path: path.yml
    - py_path: null
      yml_path:  path.yaml
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_module_function.Data(
    test_function_name=get_module_function.get_test_function_name(), 
    _module=app,
  )
  function = get_module_function.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)
    
    # Result should be instance of `Data` with the correct field values
    assert type(result).__name__ == 'Data'
    for field, expected_value in tests.expected_results[i].items():
      result_value = getattr(result, field)
      assert result_value == expected_value


def test_setup_data() -> None:
  tests = '''
    test_description: Should return a `Data` object to facilitate processing 
      downstream for different inputs into the main function
    case_descriptions:
    - a dictionary with the python file path set
    - a dictionary with the yml file path set
    - a dataclass with the python file path set
    - a dataclass with the yml file path set
    - a string for the python file path
    - a string for the yml file path
    cases:
    - data: 
        py_path: path.py
        yml_path: null
    - data: 
        py_path: null
        yml_path: path.yml
    - data: 
        py_path: path.py
        yml_path: null
    - data: 
        py_path: null
        yml_path: path.yml
    - data: path.py
    - data: path.yml
    expected_results:
    - py_path: path.py
      yml_path: null
    - py_path: null
      yml_path: path.yml
    - py_path: path.py
      yml_path: null
    - py_path: null
      yml_path: path.yml
    - py_path: path.py
      yml_path: null
    - py_path: null
      yml_path: path.yml
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_module_function.Data(
    test_function_name=get_module_function.get_test_function_name(), 
    _module=app,
  )
  function = get_module_function.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    # Convert first and second cases to Dataclasses
    if i in [0, 2]:
      _case['data'] = app.Data(**_case['data'])

    # Execute function
    result = function(**_case)
    
    # Result should be instance of `Data` with the correct field values
    assert type(result).__name__ == 'Data'
    for field, expected_value in tests.expected_results[i].items():
      result_value = getattr(result, field)
      assert result_value == expected_value


def test_get_associated_path() -> None:
  tests = '''
    test_description: Should return the python associated with a yml path, or
      vice versa
    case_descriptions:
    - Path is for `.yaml` file
    - Path for a `.yml` file
    - Path for a `.py` file
    cases:
      - data: dir/file.yaml
      - data: dir/file.yml
      - data: dir/file.py
    expected_results:
      - dir/file.py
      - dir/file.py
      - dir/file.yml
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_module_function.Data(
    test_function_name=get_module_function.get_test_function_name(), 
    _module=app,
  )
  function = get_module_function.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)
    
    # Verify that result is the correct extension
    assert result == tests.expected_results[i]


def test_set_missing_field_path() -> None:
  tests = '''
    test_description: Should fill in the missing python or yaml path in a 
      `Data` object
    case_descriptions:
    - yml path is missing
    - py path is missing and yml extension is `.yml'
    - py path is missing and yml extension is `.yaml'
    - neither path is missing
    cases:
    - data: 
       py_path: path/app.py
       yml_path: null
    - data: 
       py_path: null
       yml_path: path/app.yml
    - data: 
       py_path: null
       yml_path: path/app.yaml
    - data: 
       py_path: path/app.py
       yml_path: path/app.yaml
    expected_results:
    - yml_path: path/app.yml
      py_path: path/app.py
    - yml_path: path/app.yml
      py_path: path/app.py
    - yml_path: path/app.yaml
      py_path: path/app.py
    - yml_path: path/app.yaml
      py_path: path/app.py
  '''

  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_module_function.Data(
    test_function_name=get_module_function.get_test_function_name(), 
    _module=app,
  )
  function = get_module_function.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case['data'] = app.Data(**_case['data'])

    # Execute function
    result = function(**_case)

    # Result should be a `Data` object
    assert isinstance(result, app.Data) is True
    # Verify that the fields of the result are as expected
    for field, expected_value in tests.expected_results[i].items():
      field_value = getattr(result, field) 
      assert field_value == expected_value


def test_main() -> None:
  tests = '''
    test_description: Should return a `Data` object containing the paths to a
      associated python and yml files
    case_descriptions: Cases for string, dictionary, and dataclasses inputs
    cases:
    - data: path/app.yml
    - data: path/app.yaml
    - data: path/app.py
    - data:
        yml_path: path/app.yml
        py_path: null
    - data:
        yml_path: path/app.yaml
        py_path: null
    - data:
        yml_path: null
        py_path: path/app.py
    - data:
        yml_path: path/app.yml
        py_path: path/app.py
    - data:
        yml_path: path/app.yml
        py_path: null
    - data:
        yml_path: path/app.yaml
        py_path: null
    - data:
        yml_path: null
        py_path: path/app.py
    - data:
        yml_path: path/app.yml
        py_path: path/app.py
    expected_results:
    - yml_path: path/app.yml
      py_path: path/app.py
    - yml_path: path/app.yaml
      py_path: path/app.py
    - yml_path: path/app.yml
      py_path: path/app.py
    - yml_path: path/app.yml
      py_path: path/app.py
    - yml_path: path/app.yaml
      py_path: path/app.py
    - yml_path: path/app.yml
      py_path: path/app.py
    - yml_path: path/app.yml
      py_path: path/app.py
    - yml_path: path/app.yml
      py_path: path/app.py
    - yml_path: path/app.yaml
      py_path: path/app.py
    - yml_path: path/app.yml
      py_path: path/app.py
    - yml_path: path/app.yml
      py_path: path/app.py
  '''

  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_module_function.Data(
    test_function_name=get_module_function.get_test_function_name(), 
    _module=app,
  )
  function = get_module_function.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)

    # Result should be a `Data` object
    assert isinstance(result, app.Data) is True
    # Verify that the fields of the result are as expected
    for field, expected_value in tests.expected_results[i].items():
      field_value = getattr(result, field) 
      assert field_value == expected_value


if __name__ == '__main__':
  # Invoke pytest for this module
  pytest_arguments = sys.argv
  pytest_arguments.extend(['-x', '-s', '--verbose', '--cov', '.'])
  pytest.main()
  print(sys.argv)
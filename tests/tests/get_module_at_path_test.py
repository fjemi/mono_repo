#! /usr/bin/env python3

import sys
import pytest
from dataclasses import dataclass
from yaml import safe_load
from typing import Any, List, Dict

from app import get_module_at_path
from tests.get_module_at_path_resources import app as test_resources


# Path to the test resources directory
TEST_RESOURCES_DIR = __file__.replace('app_test.py', 'test_resources')


@dataclass
class Tests:
  test_description: str | None = None
  case_descriptions: List[Dict[str, str]] | Dict[str, str] | None = None
  cases: List[Any] | Any | None = None
  expected_results: List[Any] | Any | None = None
  expected_fields: List[bool] | bool | None = None


def test_case_setup_str_data() -> None:
  tests = '''
    test_description: Should return a `Module` object when a string is passed 
      into the main function
    case_descriptions:
    - case_0: input is a string
    - case_1: input is a string
    - case_2: input is a string
    - case_3: input is a null
    cases:
    - path_0
    - path_1
    - path_2
    - null
    expected_results:
    - path: path_0
    - path: path_1
    - path: path_2
    - path: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.case_setup_str_data(data=_case)

    # Result should be a `Module` object
    assert isinstance(result, app.Module) is True
    # Verify that the fields of the result are as expected
    for field, expected_value in tests.expected_results[i].items():
      field_value = getattr(result, field) 
      assert field_value == expected_value


def test_case_setup_dict_data() -> None:
  tests = '''
    test_description: Should return a `Module` object when a dictionary is
      passed into the main function
    case_descriptions:
    - case_0: input is a string
    - case_1: input is a string
    - case_2: input is a string
    - case_3: input is a null
    cases:
    - path: path_0
    - path: path_1
    - path: path_2
    - path: null
    expected_results:
    - path: path_0
    - path: path_1
    - path: path_2
    - path: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.case_setup_dict_data(data=_case)

    # Result should be a `Module` object
    assert isinstance(result, app.Module) is True
    # Verify that the fields of the result are as expected
    for field, expected_value in tests.expected_results[i].items():
      field_value = getattr(result, field) 
      assert field_value == expected_value


def test_case_setup_module_data() -> None:
  tests = '''
    test_description: Should return a `Module` object when a `Module` is
      passed into the main function
    case_descriptions:
    - case_0: dictionary to cast to `Module` object
    - case_1: dictionary to cast to `Module` object
    - case_2: dictionary to cast to `Module` object
    - case_3: dictionary to cast to `Module` object
    cases:
    - path: path_0
    - path: path_1
    - path: path_2
    - path: null
    expected_results:
    - path: path_0
    - path: path_1
    - path: path_2
    - path: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case = app.Module(**_case)

    # Execute function
    result = app.case_setup_module_data(data=_case)

    # Result should be a `Module` object
    assert isinstance(result, app.Module) is True
    # Verify that the fields of the result are as expected
    for field, expected_value in tests.expected_results[i].items():
      field_value = getattr(result, field) 
      assert field_value == expected_value


def test_case_setup_nonetype_data() -> None:
  tests = '''
    test_description: Should return a `Module` object when a null value is
      passed into the main function
    case_descriptions:
    - case_0: null value
    cases:
    - null
    expected_results:
    - path: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.case_setup_nonetype_data(data=_case)

    # Result should be a `Module` object
    assert isinstance(result, app.Module) is True
    # Verify that the fields of the result are as expected
    for field, expected_value in tests.expected_results[i].items():
      field_value = getattr(result, field) 
      assert field_value == expected_value


def test_setup_data() -> None:
  tests = '''
    test_description: Should return a `Module` object for different types of 
      values passed in
    case_descriptions:
    - case_0: null value
    - case_1: a string value
    - case_2: a dictionary value
    cases:
    - null
    - path_0
    - {path: path_0}
    expected_results:
    - path: null
    - path: path_0
    - path: path_0
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.setup_data(data=_case)

    # Result should be a `Module` object
    assert isinstance(result, app.Module) is True
    # Verify that the fields of the result are as expected
    for field, expected_value in tests.expected_results[i].items():
      field_value = getattr(result, field) 
      assert field_value == expected_value


def test_case_path_exists_is_true() -> None:
  tests = '''
    test_description: Should return a `Module` object for different types of 
      values passed in
    case_descriptions:
    - case_0: path to an existing module in the test resources directory
    - case_1: path to an existing module in the test resources directory
    - case_2: path to an existing module in the test resources directory
    cases:
    - path: {TEST_RESOURCES_DIR}/app_0.py
      name: test_resources.app_0
    - path: {TEST_RESOURCES_DIR}/app_1.py
      name: test_resources.app_1
    - path: {TEST_RESOURCES_DIR}/app_2.py
      name: test_resources.app_2
    expected_results:
    - __file__: {TEST_RESOURCES_DIR}/app_0.py
      __name__: test_resources.app_0
    - __file__: {TEST_RESOURCES_DIR}/app_1.py
      __name__: test_resources.app_1
    - __file__: {TEST_RESOURCES_DIR}/app_2.py
      __name__: test_resources.app_2
  '''
  # Add env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case = app.setup_data(data=_case)

    # Execute function
    result = app.case_path_exists_is_true(data=_case)

    # Result should be a `module` object
    assert type(result).__name__ == 'module'
    # Verify that the fields of the result are as expected
    for field, expected_value in tests.expected_results[i].items():
      field_value = getattr(result, field) 
      assert field_value == expected_value


def test_case_path_exists_is_false() -> None:
  tests = '''
    test_description: Should return a null `Module` object for any value passed
      in
    case_descriptions:
    - case_0: null value
    - case_1: a string value
    - case_2: a dictionary value
    cases:
    - null
    - path_0
    - {path: path_0}
    expected_results:
    - null
    - null
    - null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case = app.setup_data(_case)

    # Execute function
    result = app.case_path_exists_is_false(data=_case)

    # Result should be a `NoneType` object
    assert result is None


def test_case_name_is_none_is_false() -> None:
  tests = '''
    test_description: Should return the `name` string passed in
    case_descriptions:
    - case_0: a string
    - case_1: a string
    - case_2: a string
    cases:
    - name: name_0
      path: null
    - name: name_1
      path: null
    - name: name_2
      path: null
    expected_results:
    - name: name_0
      type: str
    - name: name_1
      type: str
    - name: name_2
      type: str
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.case_name_is_none_is_false(**_case)

    # Result should `name` string passed in
    assert result == tests.expected_results[i]['name']
    assert type(result).__name__ == tests.expected_results[i]['type']


def test_case_name_is_none_is_true() -> None:
  tests = '''
    test_description: Should return the `name` of a module in the format
      `[module_name].[folder_name]`,
    case_descriptions:
    - case_0: a string
    - case_1: a string
    - case_2: a string
    cases:
    - name: null
      path: test_resources/app_0
    - name: null
      path: test_resources/app_1
    - name: null
      path: test_resources/app_2
    expected_results:
    - name: test_resources.app_0
      type: str
    - name: test_resources.app_1
      type: str
    - name: test_resources.app_2
      type: str
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.case_name_is_none_is_true(**_case)

    # Result should be a string in the format `[module_name].[folder_name]`
    assert result == tests.expected_results[i]['name']
    assert type(result).__name__ == tests.expected_results[i]['type']


def test_main() -> None:
  tests = '''
    test_description: Should return the `Module` object at a given path if it 
      exists, otherwise an empty `Module`
    case_descriptions:
    - case_0: path to an existing module in the test resources directory
    - case_1: path to an existing module in the test resources directory
    - case_2: path to an existing module in the test resources directory
    cases:
    - path: {TEST_RESOURCES_DIR}/app_0.py
    - path: {TEST_RESOURCES_DIR}/app_1.py
    - path: {TEST_RESOURCES_DIR}/app_2.py
    - path: None
      name: None
    expected_results:
    - path: {TEST_RESOURCES_DIR}/app_0.py
      name: test_resources.app_0
    - path: {TEST_RESOURCES_DIR}/app_1.py
      name: test_resources.app_1
    - path: {TEST_RESOURCES_DIR}/app_2.py
      name: test_resources.app_2
    - path: None
      name: None
  '''
  # Add env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.main(_case)

    # # Result should be a `module` object
    assert type(result).__name__ == 'Module'
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
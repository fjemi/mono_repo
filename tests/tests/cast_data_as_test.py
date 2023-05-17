#! /usr/bin/env python3

import sys
import pytest
from random import randint
from inspect import cleandoc
from yaml import safe_load
import dacite
from dataclasses import dataclass
from pydantic import BaseModel
from typing import Any, List, Dict

from app import cast_data_as
from tests.cast_data_as_resources import app as test_resources


# Path to the test resources directory
TEST_RESOURCES_DIR = __file__.replace('app_test.py', 'test_resources')

# Use this to convert strings to objects for the test data expected results
STRING_TO_TYPE = {
  'str': str,
  'list': list,
  'dict': dict,
  'int': int,
  'float': float,
  'Pydantic_Dataclass': test_resources.Pydantic_Dataclass,
  'Basemodel':  test_resources.Basemodel,
  'Standard_Dataclass': test_resources.Standard_Dataclass,
  'None': None,
  None: None,
}


@dataclass
class Tests:
  test_description: str | None = None
  case_descriptions: List[Dict[str, str]] | Dict[str, str] | None = None
  cases: List[Any] | Any | None = None
  expected_results: List[Any] | Any | None = None
  expected_fields: List[bool] | bool | None = None


def test_setup_data_from_dict() -> None:
  # Test cases
  tests = '''
    test_description: Should return a dataclass for the case where the input 
      is a dictionary
    case_descriptions:
    - case_1: A dictionary containing all of the fields for the `Data` dataclass
        within the `app` module
    cases:
    - values: null
      values_n: null
      constructors: null
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
    expected_results:
    - values: null
      values_n: null
      constructors: null
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  # Running test data through function
  for i in range(len(tests.cases)):
    data = tests.cases[i]
    result = app.case_setup_data_from_dict(data=data)
    assert result.__dict__ == tests.expected_results[i]
    assert type(result).__name__ == 'Data'


def test_setup_data_from_data() -> None:
  '''Should return a dataclass for cases where the input is a dataclass'''
  # Test cases
  tests = '''
    cases:
    - values: null
      values_n: null
      constructors: null
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
    expected_results:
    - values: null
      values_n: null
      constructors: null
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  # Running test data through function
  for i in range(len(tests.cases)):
    data = app.Data(**tests.cases[i])
    result = app.case_setup_data_from_data(data=data)
    assert result == app.Data(**tests.expected_results[i])
    assert type(result).__name__ == 'Data'


def test_setup_data() -> None:
  '''
  Should return the `Data` object from the the `app` module for inputs of type 
  `dict` and `Data`.
  '''
  # Test cases
  tests = '''
    cases:
    - values: null
      values_n: null
      constructors: null
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
    expected_results:
    - values: null
      values_n: null
      constructors: null
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  # Running test data through function
  for i in range(len(tests.cases)):
    results = dict(
      dictionary=app.setup_data(data=tests.cases[i]),
      dataclass=app.setup_data(data=app.Data(**tests.cases[i])),
    )
    # Should produce the same dataclass for 
    # matching dataclass and dict inputs
    assert results['dictionary'] == results['dataclass']
    assert results['dictionary'].__dict__ == tests.expected_results[i]
    assert results['dataclass'].__dict__ == tests.expected_results[i]


def test_case_value_is_list_is_false() -> None:
  tests = '''
    case_descriptions:
    - case_0: A single integer
    - case_1: A single string
    - case_2: A single float
    cases:
    - value: 0
    - value: test
    - value: 2.0
    expected_results:
    - [0]
    - [test]
    - [2.0]
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  # Running test data through function
  for i in range(len(tests.cases)):
    data = tests.cases[i]
    result = app.case_value_is_list_is_false(**data)
    assert result == tests.expected_results[i]


def test_case_value_is_list_is_true() -> None:
  tests = '''
    case_descriptions:
    - case_0: A list of integer
    - case_1: A list containing a single string
    - case_2: A list of floats
    cases:
    - value: [0, 1, 2]
    - value: [test_0]
    - value: [1.0, 2.0]
    expected_results:
    - [0, 1, 2]
    - [test_0]
    - [1.0, 2.0]
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  # Running test data through function
  for i in range(len(tests.cases)):
    data = tests.cases[i]
    result = app.case_value_is_list_is_true(**data)
    assert result == tests.expected_results[i]


def test_convert_single_item_to_list() -> None:
    # Test cases
  tests = '''
    case_descriptions:
    - case_00: Single items for values and constructors fields
    - case_01: List of items for values and constructor fields
    cases:
    - values: null
      values_n: null
      constructors: null
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
    - values: [null, null]
      values_n: null
      constructors: [null, null]
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
    expected_results:
    - values: [null]
      values_n: null
      constructors: [null]
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
    - values: [null, null]
      values_n: null
      constructors: [null, null]
      constructors_n: null
      modules: null
      casted_values: null
      value_and_cast_type_cases: null
      cast_function_names: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  # Running test data through function
  for i in range(len(tests.cases)):
    data = app.Data(**tests.cases[i])
    result = app.convert_single_item_to_list(
      data=data, 
    _locals=vars(app),
    )
    assert result.__dict__ == tests.expected_results[i]


def test_get_field_lengths() -> None:
  '''
  Should return the dataclass `N` with the
  correct lengths for the values and constructors lists
  '''
  # Test data in YML format
  data = '''
    expected_results:
    - values_n: 1
      constructors_n: 1
    - values_n: 2
      constructors_n: 2
    - values_n: 3
      constructors_n: 3
    cases:
    - values: [value_00]
      constructors: 
      - name: constructor_00
    - values: [value_00, value_01]
      constructors:
      - name: constructor_00
      - name: constructor_01
    - values: [value_00, value_01, value_02]
      constructors:
      - name: constructor_00
      - name: constructor_01
      - name: constructor_02
  '''
  # Load test data into dataclass
  data = safe_load(data)
  data = Tests(**data)
  # Run test data through function
  for i in range(len(data.cases)):
    _case = data.cases[i]
    _case = dacite.from_dict(app.Data, _case)
    result = app.get_field_lengths(data=_case)
    # Verify expected values for certain fields of 
    # the resulting dataclass
    for field, expected_value in data.expected_results[i].items():
      result_value = getattr(result, field)
      assert result_value == expected_value


def test_case_zero_to_one_or_many_relationship() -> None:
  '''
  Should create a list of n null constructor objects
  '''
  # Test cases
  tests = '''
    case_descriptions:
    - case_0: Zero to one relationship between constructors and values
    - case_1: Zero to two relationship between constructors and values
    - case_2: Zero to three relationship between constructors and values
    cases:
    - values_n: 1
      constructors_n: null
    - values_n: 2
      constructors_n: null
    - values_n: 3
      constructors_n: null
    expected_results:
    - constructors: 
      - name: null
    - constructors:  
      - name: null
      - name: null
    - constructors:  
      - name: null 
      - name: null
      - name: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  # Running test data through function
  for i in range(len(tests.cases)):
    data = app.Data(**tests.cases[i])
    expected_result = dacite.from_dict(app.Data, tests.expected_results[i])
    result = app.case_zero_to_one_or_many_relationship(
      constructors=data.constructors,
      values_n=data.values_n,
    )
    # Result produce lists of null constructor objects
    assert result == expected_result.constructors
    assert result.count(app.Constructor()) == data.values_n


def test_case_one_to_one_relationship() -> None:
  '''
  Should return the constructors list
  passed into the function
  '''
  # Test cases
  tests = '''
    case_descriptions:
    - case_0: one to one relationship between constructors and values
    - case_1: two to two relationship between constructors and values
    - case_2: three to three relationship between constructors and values
    cases:
    - values_n: 1
      constructors: 
      - name: constructor_0
    - values_n: 2
      constructors:
      - name: constructor_0
      - name: constructor_0
    - values_n: 3
      constructors:
      - name: constructor_0
      - name: constructor_0
      - name: constructor_0
    expected_results:
    - constructors: 
      - name: constructor_0
    - constructors: 
      - name: constructor_0
      - name: constructor_0
    - constructors:
      - name: constructor_0
      - name: constructor_0
      - name: constructor_0
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  # Running test data through function
  for i in range(len(tests.cases)):
    data = app.setup_data(tests.cases[i])
    expected_result = app.setup_data(tests.expected_results[i])
    result = app.case_one_to_one_relationship(
      constructors=data.constructors,
      values_n=data.values_n,
    )
    # Result produce lists of null constructor objects
    assert result == expected_result.constructors
    assert result.count(
      app.Constructor(name='constructor_0')) == data.values_n


def test_case_many_to_many_relationship() -> None:
  '''
  Should return the constructors list
  passed into the function
  '''
  # Test cases
  tests = '''
    case_descriptions:
    - case_0: one to one relationship between constructors and values
    - case_1: two to two relationship between constructors and values
    - case_2: three to three relationship between constructors and values
    cases:
    - values_n: null
      constructors: null
    - values_n: null
      constructors: null
    - values_n: null
      constructors: null
    expected_results:
    - exception: RunTime
      message: null
    - exception: RunTime
      message: null
    - exception: RunTime
      message: null
  '''
  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  # Running test data through function
  for i in range(len(tests.cases)):
    data = dacite.from_dict(app.Data, tests.cases[i])
    # Should raise an exception
    # TODO - https://stackoverflow.com/questions/23337471/how-to-properly-assert-that-an-exception-gets-raised-in-pytest
    exception = tests.expected_results[i]
    with pytest.raises(Exception) as e_info:
      result = app.case_many_to_many_relationship(
        constructors=data.constructors,
        values_n=data.values_n,
      )


def test_case_one_to_many_relationship() -> None:
  '''
  Should return expanded a list with one item to contain
  n of those items

  '''
  values_n = randint(0, 10)
  constructors = ['constructors']
  result = app.case_one_to_many_relationship(
    constructors=constructors,
    values_n=values_n,
  )
  assert len(result) == values_n
  assert result.count(constructors[0]) == values_n


def test_match_constructors_to_values_relationship() -> None:
  tests = '''
    test_description: Should return a list of constructors. The length of the 
      list should match the length of the values field. Should raise an error 
      otherwise
    case_descriptions:
    - case_0: One to one
    - case_1: One to many 
    - case_2: One to one 
    - case_3: Zero to one
    - case_4: Zero to many
    - case_5: None to one
    - case_6: None to many 
    cases:
    - values_n: 1
      constructors_n: 1
      constructors:
      - name: constructor_0
    - values_n: 2
      constructors_n: 1
      constructors:
      - name: constructor_0
    - values_n: 3
      constructors_n: 3
      constructors:
      - name: constructor_0
      - name: constructor_1
      - name: constructor_2
    - values_n: 1
      constructors_n: 0
      constructors: null
    - values_n: 1
      constructors_n: 1
      constructors:
      - name: constructor_0
    - values_n: 1
      constructors_n: 0
      constructors: null
    - values_n: 3
      constructors_n: 0
      constructors: []
    expected_results:
    - constructors:
      - name: constructor_0
    - constructors:
      - name: constructor_0
      - name: constructor_0
    - constructors:
      - name: constructor_0
      - name: constructor_1
      - name: constructor_2
    - constructors: 
      - name: null
    - constructors:
      - name: constructor_0
    - constructors: 
      - name: null
    - constructors:
      - name: null
      - name: null
      - name: null
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Format test data and execute function with data from the test case
    _case = app.setup_data(tests.cases[i])
    result = app.match_constructors_to_values_relationship(data=_case)
    # Format the expected result for the test
    expected_result = app.setup_data(tests.expected_results[i])
    # Verify that individual fields of the result are as expected
    for field in tests.expected_results[i]:
      field_result = getattr(result, field)
      field_result_expected = getattr(expected_result, field)
      assert field_result == field_result_expected
    

def test_set_modules_and_add_standard_library() -> None:
  tests = '''
    test_description: Should load a module at a valid path and return the module
      in a list with the standard library, both as `Module` objects
    case_descriptions:
    - case_0:
    - case_1: 
    cases:
    # - path: null
    - path: {TEST_RESOURCES_DIR}/app.py
      name: null
    expected_results: null
    # # - path: null
    # - - path: {TEST_RESOURCES_DIR}/app.py
    #     name: test_resources.app
    #     _object: null
    #   - path: standard_library
    #     name: standard_library
    #     _object:
  '''
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Format test data and execute function with data from the test case
    _case = app.Module(**tests.cases[i])
    result = app.set_modules_and_add_standard_library(module=_case)
    # Result should have these modules names and objects that are not `None`
    module_names = ['test_resources.app', 'standard_library']
    for i in range(len(result)):
      assert result[i].name == module_names[i]
      assert result[i]._object is not None


def test_case_module_is_a_dict() -> None:
  tests = '''
    test_description: Should return a constructor. If the name of the 
      constructor is in a module's, represented as dictionary, keys then the
      constructors's object is set to the value associated with the key.
    case_descriptions:
    - case_0: Constructor name is null
    - case_1: Constructor name is not in dictionary keys
    - case_2: Constructor name is in dictionary keys
    - case_3: Constructor name is in dictionary keys
    - case_4: Constructor name is in dictionary keys
    cases:
    - module: 
        _object: {str: str, int: int, float: float}
      constructor:
        name: null
    - module: 
        _object: {str: str, int: int, float: float}
      constructor:
        name: name_not_in_module_keys
    - module: 
        _object: {str: str, int: int, float: float}
      constructor:
        name: str
    - module: 
        _object: {str: str, int: int, float: float}
      constructor:
        name: int
    - module: 
        _object: {str: str, int: int, float: float}
      constructor:
        name: float
    expected_results:
    - _object: null
    - _object: null
    - _object: str
    - _object: int
    - _object: float
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    _case = tests.cases[i]
    # Setup
    _case['constructor'] = app.Constructor(**_case['constructor'])
    _case['module'] = app.Module(**_case['module'])

    # Execute function
    result = app.case_module_is_a_dict(**_case)
    print(result)
    # Resulting constructor object should be the 
    # correct type and value when casted to string
    assert type(result).__name__ == 'Constructor'
    assert result._object == tests.expected_results[i]['_object']


def test_case_module_is_a_module() -> None:
  tests = '''
    test_description: Should return a constructor. If the name of the 
      constructor is in a module's attributes return the constructor with the
      value of the attribute. Otherwise return the original constructor.
    case_descriptions:
    - case_0: Constructor name is null
    - case_1: Constructor name is not in module attributes
    - case_2: Constructor name, Standard_Dataclass, is in module attributes
    - case_3: Constructor name, Basemodel, is in module attributes
    - case_4: Constructor name, Pydantic_Dataclass, is in module attributes
    cases:
    - module: 
        _object: {test_resources}
      constructor:
        name: null
    - module: 
        _object: {test_resourses_app}
      constructor:
        name: name_is_not_an_attribute
    - module: 
        _object: {test_resources}
      constructor:
        name: Standard_Dataclass
    - module: 
        _object: {test_resources}
      constructor:
        name: Basemodel
    - module: 
        _object: {test_resources}
      constructor:
        name: Pydantic_Dataclass
    expected_results:
    - value_as_str: None
    - value_as_str: None
    - value_as_str: <class 'test_resources.app.Standard_Dataclass'>
    - value_as_str: <class 'test_resources.app.Basemodel'>
    - value_as_str: <class 'test_resources.app.Pydantic_Dataclass'>
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    _case = tests.cases[i]
    # Setup
    _case['constructor'] = app.Constructor(**_case['constructor'])
    _case['module'] = app.Module(**_case['module'])
    _case['module']._object = test_resources

    # Execute function
    result = app.case_module_is_a_module(**_case)

    # Resulting constructor object should be the 
    # correct type and value when casted to string
    assert type(result).__name__ == 'Constructor'
    assert str(result._object) == tests.expected_results[i][
      'value_as_str']


def test_get_constructor_objects() -> None:
  tests = '''
    test_description:
    case_descriptions:
    cases:
    - constructors:
      - name: str
        _object: null
      values_n: 1
      modules:
      - name: standard_library
    - constructors:
      - name: str
        _object: null
      - name: int
        _object: null
      values_n: 2
      modules:
      - name: standard_library
    - constructors:
      - name: str
        _object: null
      - name: int
        _object: null
      - name: float
        _object: null
      values_n: 3
      modules:
      - name: standard_library
    expected_results: 
    - [str]
    - [str, int]
    - [str, int, float]
  '''
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)
  
  for i in range(len(tests.cases)):
    # Format test data and execute function with data from the test case
    _case = app.setup_data(data=tests.cases[i])
    _case.modules[0]._object = __builtins__
    result = app.get_constructor_objects(
      constructors=_case.constructors,
      values_n=_case.values_n,
      modules=_case.modules
    )
    # Verify constructor objects types from function results
    expected_result = tests.expected_results[i]
    for j in range(len(result)):
      constructor = result[j]
      _type = str(constructor._object)
      assert _type.find(expected_result[j]) != -1


def test_case_value_to_value() -> None:
  tests = '''
    test_description: Should return the value passed in. 
    case_descriptions:
    - case_0: Value is a int
    - case_1: Value is a string
    - case_2: Value is a float
    - case_3: Value is a list
    - case_4: Value is a dictionary
    - case_5: Value is a null
    cases:
    - 1
    - '1'
    - 1.0
    - - 0
        1
        2
    - 0: 0
      1: 1
      2: 2
    expected_results:
    - 1
    - '1'
    - 1.0
    - - 0
        1
        2
    - 0: 0
      1: 1
      2: 2
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.case_value_to_value(
      constructor=None,
      value=_case,
    )

    # Result should return the value passed in
    assert result == tests.expected_results[i]


def test_case_cast_no_unpacking() -> None:
  tests = '''
    test_description: Should return a value cast to a constructor object. 
    case_descriptions:
    - case_0: Integer to string
    - case_1: String to integer
    - case_2: Integer to float
    cases:
    - constructor:
        name: str
      value: 1
    - constructor:
        name: int
      value: '1'
    - constructor:
        name: float
      value: 2
    expected_results:
    - type: str
      value: '1'
    - type: int
      value: 1
    - type: float
      value: 2.0
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    constructor = app.Constructor(**_case['constructor'])
    constructor._object = __builtins__[constructor.name]

    # Execute function
    result = app.case_cast_no_unpacking(
      constructor=constructor,
      value=_case['value'],
    )

    # Result should correct value and type
    assert result == tests.expected_results[i]['value']
    assert type(result).__name__ == tests.expected_results[i]['type']


def test_case_pydantic_initialised_in_dict_keys_is_true() -> None:
  tests = '''
    test_description:
    case_descriptions:
    - case_1: Empty dictionary with field removed
    - case_2: Dictionary with one key with field removed
    - case_3: Dictionary with two keys with field removed
    cases:
    - __pydantic_initialised__: null
    - a: 0
      __pydantic_initialised__: null
    - a: 0
      b: 0
      __pydantic_initialised__: null
    expected_results:
    - {}
    - a: 0
    - a: 0
      b: 0
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    # Execute function
    result = app.case_pydantic_initialised_in_dict_keys_is_true(data=_case)
    # Verify results
    assert result == tests.expected_results[i]
    assert isinstance(result, dict)


def test_case_pydantic_initialised_in_dict_keys_is_false() -> None:
  tests = '''
    test_description: Should act as a pass through function and return the 
      dictionary passed in
    case_descriptions:
    - case_1: Empty dictionary
    - case_2: Dictionary with one key
    - case_3: Dictionary with two keys
    cases:
    - {}
    - a: 0
    - a: 0
      b: 0
    expected_results:
    - {}
    - a: 0
    - a: 0
      b: 0
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    # Execute function
    result = app.case_pydantic_initialised_in_dict_keys_is_false(data=_case)
    # Verify results
    assert result == tests.expected_results[i]
    assert isinstance(result, dict)

    
def test_case_basemodel_or_dataclass_to_dict() -> None:
  tests = '''
    test_description: Should convert basemodel and dataclass values passed in to 
      dictionaries
    case_descriptions:
    - case_0: basemodel_object
    - case_1: pydantic_dataclass_object
    - case_2: standard_dataclass_object
    cases:
    - _object: Standard_Dataclass
      data:
        a: 0
        b: 0
    - _object: Basemodel
      data:
        a: 0
        b: 0
    - _object: Pydantic_Dataclass
      data:
        a: 0
        b: 0
    expected_results:
    - a: 0
      b: 0
    - a: 0
      b: 0
    - a: 0
      b: 0
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _object = getattr(test_resources, _case['_object'])
    data = _case['data']
    data = _object(**data)
    # Execute function
    result = app.case_basemodel_or_dataclass_to_dict(
      constructor=None,
      value=data,
    )
    # Result should be a dictionary
    assert result == tests.expected_results[i]
    assert isinstance(result, dict)


def test_case_dict_to_dataclass_or_basemodel() -> None:
  tests = '''
    test_description: Should return the result of casting a dictionary to a 
      constructor object that is a basemodel and dataclass
    case_descriptions:
    - case_0: basemodel_object
    - case_1: pydantic_dataclass_object
    - case_2: standard_dataclass_object
    cases:
    - constructor:
        name: Standard_Dataclass
      data:
        a: 0
        b: 0
    - constructor:
        name: Basemodel
      data:
        a: 0
        b: 0
    - constructor:
        name: Pydantic_Dataclass
      data:
        a: 0
        b: 0
    expected_results:
    - type: Standard_Dataclass
      data:
        a: 0
        b: 0
    - type: Basemodel
      data:
        a: 0
        b: 0
    - type: Pydantic_Dataclass
      data:
        a: 0
        b: 0
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    data = _case['data']
    constructor = app.Constructor(**_case['constructor'])
    constructor._object = getattr(test_resources, constructor.name)
    # Execute function
    result = app.case_dict_to_dataclass_or_basemodel(
      constructor=constructor,
      value=data,
    )
    # Result should be a basemodel or dataclass 
    assert type(result).__name__ == tests.expected_results[i]['type']
    # Results should have the correct values
    for key, value in tests.expected_results[i]['data'].items():
      assert getattr(result, key) == value


def test_case_list_or_tuple_to_dataclass() -> None:
  tests = '''
    test_description: Should return the result of casting a list or tuple to a 
      constructor object that is a basemodel and dataclass
    case_descriptions:
    - case_0: basemodel_object
    - case_1: pydantic_dataclass_object
    - case_2: standard_dataclass_object
    cases:
    - constructor:
        name: Standard_Dataclass
      data: [0, 0]
    - constructor:
        name: Pydantic_Dataclass
      data: [2, 2]
    expected_results:
    - type: Standard_Dataclass
      data:
        a: 0
        b: 0
    - type: Pydantic_Dataclass
      data:
        a: 2
        b: 2
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    data = _case['data']
    constructor = app.Constructor(**_case['constructor'])
    constructor._object = getattr(test_resources, constructor.name)

    # Execute function
    result = app.case_list_or_tuple_to_dataclass(
      constructor=constructor,
      value=data,
    )

    # Result should be a basemodel or dataclass 
    assert type(result).__name__ == tests.expected_results[i]['type']
    # Results should have the correct values
    for key, value in tests.expected_results[i]['data'].items():
      assert getattr(result, key) == value


def test_case_list_or_tuple_to_dict() -> None:
  tests = '''
    test_description: Should return dictionary from a list of lists or tuple of 
      tuples in the formats [[key, value]] and ((key, value))
    case_descriptions:
    - case_0: list
    - case_1: list
    cases:
    - - [0, 0]
      - [1, 1]
      - [2, 2]
    - - [key_0, value_0]
      - [key_1, value_1]
      - [key_2, value_2]
    expected_results:
    - 0: 0
      1: 1
      2: 2
    - key_0: value_0
      key_1: value_1
      key_2: value_2
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.case_list_or_tuple_to_dict(
      constructor=None,
      value=_case,
    )

    # Result should be a dictionary with the correct key/values
    assert result == tests.expected_results[i]


def test_case_list_or_tuple_to_dict() -> None:
  tests = '''
    test_description: Should return dictionary from a list of lists or tuple of 
      tuples in the formats [[key, value]] and ((key, value))
    case_descriptions:
    - case_0: list
    - case_1: list
    cases:
    - - [0, 0]
      - [1, 1]
      - [2, 2]
    - - [key_0, value_0]
      - [key_1, value_1]
      - [key_2, value_2]
    expected_results:
    - 0: 0
      1: 1
      2: 2
    - key_0: value_0
      key_1: value_1
      key_2: value_2
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = app.case_list_or_tuple_to_dict(
      constructor=None,
      value=_case,
    )

    # Result should be a dictionary with the correct key/values
    assert result == tests.expected_results[i]


def test_get_value_and_cast_type_cases() -> None:
  tests = '''
    test_description: Should return a list of strings. The strings should be in
      the format `<value type>_to_<constructor type>`
    case_descriptions:
    - case_0: integer to a string
    - case_1: integer to none 
    - case_2: integer to integer
    - case_3: list to list
    - case_4: list to dict
    - case_5: standard dataclass to dict
    - case_6: basemodel to dict
    - case_7: dict to pydantic dataclass
    - case_8: dict to basemodel
    - case_9: dict to standard dataclass
    - case_10: dict to dict
    cases:
    - values: 
      - 1
      - 2
      - 1
      - [0, 1, 2]
      - {0: 0, 1: 1, 2: 2}
      - Standard_Dataclass()
      - Basemodel()
      - {a: 0, b: 1}
      - {a: 0, b: 1}
      - [0, 1]
      - [[0, 0], [1, 1], [2, 2]]
      constructors:
      - name: str
      - name: None
      - name: int
      - name: list
      - name: dict
      - name: dict
      - name: dict
      - name: Pydantic_Dataclass
      - name: Basemodel
      - name: Standard_Dataclass
      - name: dict
      values_n: 10
    expected_results:
    - - other_to_other
      - other_to_none
      - other_to_other
      - list|tuple_to_list|tuple
      - dict_to_dict
      - dataclass_to_dict
      - basemodel_to_dict
      - dict_to_dataclass
      - dict_to_basemodel
      - list|tuple_to_dataclass
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case = app.setup_data(data=_case)
    for j in range(len(_case.values)):
      # Convert string instances to dataclasses or basemodels
      if _case.values[j] == 'Basemodel()':
        _case.values[j] = test_resources.Basemodel(a=1, b=1)
      if _case.values[j] == 'Standard_Dataclass()':
        _case.values[j] = test_resources.Standard_Dataclass(a=0, b=1)
      # Set constructor objects
      _case.constructors[j]._object = STRING_TO_TYPE[_case.constructors[j].name]

    # Execute function
    result = app.get_value_and_cast_type_cases(
      constructors=_case.constructors,
      values=_case.values,
      values_n=_case.values_n
    )

    # Result should be a list of strings in 
    # the correct format: `<value_type>_to_<constructor_type>`
    assert result == tests.expected_results[i]


def test_get_cast_function_names() -> None:
  tests = '''
    test_description: Should return a list of function names associated with
      casting a value to a constructor by type
    case_descriptions:
    - case_0: Other to other
    - case_1: Other to None
    - case_2: Other to other
    - case_3: list to list
    - case_4: dict to dict
    - case_5: dataclass to dict
    - case_6: basemodel to dict
    - case_7: dict to dataclass
    - case_8: dict to basemodel
    - case_9: tuple to dataclass
    cases:
    - value_and_cast_type_cases:
      - other_to_other
      - other_to_none
      - other_to_other
      - list|tuple_to_list|tuple
      - dict_to_dict
      - dataclass_to_dict
      - basemodel_to_dict
      - dict_to_dataclass
      - dict_to_basemodel
      - list|tuple_to_dataclass
      values_n: 10
    expected_results:
    - - case_cast_no_unpacking
      - case_value_to_value
      - case_cast_no_unpacking
      - case_value_to_value
      - case_value_to_value
      - case_basemodel_or_dataclass_to_dict
      - case_basemodel_or_dataclass_to_dict
      - case_dict_to_dataclass_or_basemodel
      - case_dict_to_dataclass_or_basemodel
      - case_list_or_tuple_to_dataclass
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Execute function
    result = app.get_cast_function_names(**tests.cases[i])

    # Result should be a list function names associated 
    # with casting a value to constructor
    assert result == tests.expected_results[i]


def test_get_casted_values() -> None:
  tests = '''
    test_description: Should return a list of values casted to constructors
    case_descriptions:
    - case_0: integer to string
    - case_1: string to integer
    - case_2: integer to float
    - case_3: integer to None
    - case_4: string to string
    - case_5: dataclass to dict
    - case_6: basemodel to dict
    - case_7: dict to pydantic dataclass
    - case_8: dicto to basemodel
    - case_9: dict to standard dataclass
    cases:
    - cast_function_names:
      - case_cast_no_unpacking
      - case_cast_no_unpacking
      - case_cast_no_unpacking
      - case_value_to_value
      - case_cast_no_unpacking
      - case_basemodel_or_dataclass_to_dict
      - case_basemodel_or_dataclass_to_dict
      - case_dict_to_dataclass_or_basemodel
      - case_dict_to_dataclass_or_basemodel
      - case_list_or_tuple_to_dataclass
      values: 
      - 1
      - '02'
      - 3
      - 4
      - string
      - Standard_Dataclass()
      - Basemodel()
      - {b: 0, a: 1}
      - {b: 0, a: 1}
      - [0, 1]
      values_n: 10
      constructors:
      - name: str
      - name: int
      - name: float
      - name: null
      - name: str
      - name: dict
      - name: dict
      - name: Pydantic_Dataclass
      - name: Basemodel
      - name: Standard_Dataclass
    expected_results:
    - value_as_str: '1'
      type: str
    - value_as_str: '2'
      type: int
    - value_as_str: '3.0'
      type: float
    - value_as_str: '4'
      type: int
    - value_as_str: string
      type: str
    - value_as_str: "{'a': 0, 'b': 1}"
      type: dict
    - value_as_str: "{'a': 1, 'b': 1}"
      type: dict
    - value_as_str: Pydantic_Dataclass(a=1, b=0)
      type: Pydantic_Dataclass
    - value_as_str: a=1 b=0
      type: Basemodel
    - value_as_str: Standard_Dataclass(a=0, b=1)
      type: Standard_Dataclass
  '''
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case = app.setup_data(data=_case)
     
    for j in range(len(_case.constructors)):
      # Set constructor objects
      _case.constructors[j]._object = STRING_TO_TYPE[_case.constructors[j].name]
       # Convert value objects to dataclasses or basemodels
      if _case.values[j] == 'Basemodel()':
        _case.values[j] = test_resources.Basemodel(a=1, b=1)
      if _case.values[j] == 'Standard_Dataclass()':
        _case.values[j] = test_resources.Standard_Dataclass(a=0, b=1)

    # Execute function
    result = app.get_casted_values(
      constructors=_case.constructors,
      cast_function_names=_case.cast_function_names,
      values=_case.values,
      values_n=_case.values_n,
    )

    for j in range(len(result)):
      # Result should be a list of strings; constructor to value types
      assert type(result[j]).__name__ == tests.expected_results[j]['type']
      assert str(result[j]) == tests.expected_results[j]['value_as_str']


def test_main() -> None:
  tests = '''
    test_description: 
    case_descriptions:
    -
    cases:
    - values:
      - 1
      - a: 1
        b: 1
      - 1
      - [[0, 0], [1, 1]]
      - null
      - Basemodel()
      - Standard_Dataclass()
      - [0, 1, 2]
      constructors:
      - name: str
      - name: Standard_Dataclass
      - name: null
      - name: dict
      - name: null
      - name: dict
      - name: dict
      - name: list
      modules:
        path: {TEST_RESOURCES_DIR}/app.py
    expected_results:
    - value_as_str: '1'
      type: str
    - value_as_str: Standard_Dataclass(a=1, b=1)
      type: Standard_Dataclass
    - value_as_str: '1'
      type: int
    - value_as_str: '{0: 0, 1: 1}'
      type: dict
    - value_as_str: None
      type: NoneType
    - value_as_str: "{'a': 1, 'b': 1}"
      type: dict
    - value_as_str: "{'a': 0, 'b': 1}"
      type: dict
    - value_as_str: '[0, 1, 2]'
      type: list
  '''
  # Set environment variables
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)
  # Load test data from YAML into a dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case = app.setup_data(data=_case)
    
    for j in range(len(_case.values)):
      # Setup values
      # Convert value objects to dataclasses or basemodels
      if _case.values[j] == 'Basemodel()':
        _case.values[j] = test_resources.Basemodel(a=1, b=1)
      if _case.values[j] == 'Standard_Dataclass()':
        _case.values[j] = test_resources.Standard_Dataclass(a=0, b=1)
            
    # Execute function with data
    results = app.main(data=_case)
    
    # Results should be the correct type and value casted to a string
    for j in range(len(results)):
      assert str(results[j]) == tests.expected_results[j]['value_as_str']
      assert type(results[j]).__name__ == tests.expected_results[j]['type']


if __name__ == '__main__':
  # Invoke pytest for this module
  pytest_arguments = sys.argv
  pytest_arguments.extend(['-x', '-s', '--verbose'])
  pytest.main()
  print(sys.argv)
#! /usr/bin/env python3

import sys
import pytest
from dataclasses import dataclass, asdict
from yaml import safe_load
from typing import Any, List, Dict
from random import randint

from shared.patch_object import app
from shared.get_function_to_test import app as get_function_to_test
from shared.untested_test_cases import app as test_cases

from test_resources import app as test_resources


# Path to the test resources directory
TEST_RESOURCES_DIR = __file__.replace('app_test.py', 'test_resources')

# Global variable to store `object_hierarchy` for use during tests, and make sure
# they don't get overwritten
OBJECT_HIERARCHY = dict(original=[], patched=[])


LOCALS = locals()
@pytest.fixture(scope='session')
def get_locals():
  '''Locals gets overridden during tests. Using fixture and global variable
  so that each test starts with correct version of `locals()`'''
  return LOCALS


@dataclass(slots=True)
class Tests:
  test_description: str | None = None
  case_descriptions: List[Dict[str, str]] | Dict[str, str] | None = None
  cases: List[Any] | Any | None = None
  expected_results: List[Any] | Any | None = None


def test_setup_data() -> None:
  tests = '''
    test_description: Should return a dataclass with the correct fields from 
      a dictionary or dataclass input
    case_descriptions:
    - an empty dictionary
    - a nonempty dictionary
    - a dataclass
    cases:
    - data: {}
    - data: {}
    expected_results:
    - object_hierarchies: []
      patches: []
      patched: []
      reverted: []
    - object_hierarchies: []
      patches: []
      patched: []
      reverted: []

  '''
  # set env vars
  # tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    if i == 1:
      _case['data'] = app.Data(**_case['data'])

    # Execute function
    result = function(**_case)
    
    # Verify that result is the correct extension
    assert type(result).__name__ == 'Data'
    for field, expected_value in tests.expected_results[i].items():
      result_value = getattr(result, field)
      assert result_value == expected_value


def test_single_field_items_to_list() -> None:
  tests = '''
    test_description: Should convert fields whose values are a single item to
      a list containing the item
    case_descriptions:
    - a single patch object
    - a list containing a single patch object
    - a list containing two patch objects
    cases:
    - data:
        patches:
          function_name: function_name
          return_value: return_value
    - data: 
        patches:
        - function_name: function_name
          return_value: return_value
    - data: 
        patches:
        - function_name: function_name_0
          return_value: return_value_0
        - function_name: function_name_1
          return_value: return_value_1
    expected_results:
    - patches: 
      - function_name: function_name
        return_value: return_value
    - patches: 
      - function_name: function_name
        return_value: return_value
    - patches: 
      - function_name: function_name_0
        return_value: return_value_0
      - function_name: function_name_1
        return_value: return_value_1
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case['data'] = app.Data(**_case['data'])

    # Execute function
    result = function(**_case)
    
    # Verify results
    assert isinstance(result, app.Data) is True
    for field, expected_value in tests.expected_results[i].items():
      result_value = getattr(result, field)
      assert result_value == expected_value


def test_case_bind_return_value() -> None:
  tests = '''
    test_description: Result should be a function that returns a 
      `return value` when the function is called with any combination of 
      arguments
    case_descriptions:
    - return value is an integer
    - return value is a string
    - return value is a string
    - return value is a list
    cases:
    - return_value: 0
    - return_value: '1'
    - return_value: two
    - return_value: [three]
    expected_results:
    - arguments: [0]
      value: 0
    - arguments: [0, 1]
      value: '1'
    - arguments: [0, 1, 2]
      value: two
    - arguments: [0, 1, 2, 3]
      value: [three]
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)
  
    # Result should be a function
    assert type(result).__name__ == 'function'
    # Function should produce the correct output
    arguments = tests.expected_results[i]['arguments']
    assert result(*arguments) == tests.expected_results[i]['value']


def test_get_side_effect_value_and_increment_count() -> None:
  tests = '''
    test_description: Should return a side effect at index `count` and increment
      `count`. If `count` exceeds the number of side effect values its reset to
      zero
    case_descriptions: side effect values and count set at 0
    cases:
    - side_effect: 
        values: [0]
        count: 0
    - side_effect: 
        values: [0, 1, 2, 3]
        count: 0
    - side_effect: 
        values: [one, two, three, four]
        count: 0
    - side_effect: 
        values: [a, b, c]
        count: 0
    expected_results:
    - [0, 0]
    - [0, 1, 2, 3, 0]
    - [one, two, three, four, one]
    - [a, b, c, a]
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  # Set side effect as a global variable
  for i in range(len(tests.cases)):
    # Setup
    side_effect = tests.cases[i]['side_effect']
    n = len(side_effect['values'])

    # Call the function n + 1 times. The count 
    # should be reset after the n + 1 call
    result = []
    for j in range(n + 1):
      result.append(function(side_effect=side_effect))
    # Results of calling the function should be correct
    assert result == tests.expected_results[i]


def test_case_bind_side_effect_list() -> None:
  tests = '''
    test_description: Should set side effect values and counter as a global 
      variable and return the function 
      `get_side_effect_value_and_increment_count` as a lambda
    case_descriptions: return values for the function created
    cases:
    - side_effect: [0]
    - side_effect: [0, 1, 2]
    - side_effect: [one, two, three]
    - side_effect: [a, b, c]
    expected_results:
    - globals:
        side_effect: 
          values: [0]
          count: 0
      function_name: <lambda>
    - globals:
        side_effect: 
          values: [0, 1, 2]
          count: 0
      function_name: <lambda>
    - globals:
        side_effect: 
          values: [one, two, three]
          count: 0
      function_name: <lambda>
    - globals:
        side_effect: 
          values: [a, b, c]
          count: 0
      function_name: <lambda>
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    # _case = app.Data(**_case['data'])
    from test_resources import app as test

    # Execute function
    result = function(**_case)
    
    # Result should be a lambda function
    assert type(result).__name__ == 'function'
    assert result.__name__ == tests.expected_results[i]['function_name']
    # Globals should have the side effect values and counter
    # TODO: Update test to search for the global side effect variable

  
def test_case_bind_side_effect_dict() -> None:
  tests = '''
    test_description: Should return function that acts as a dictionary side 
      effect
    case_descriptions: dictionary side effects
    cases:
    - side_effect: {0: 0}
    - side_effect: {0: 0, 1: 1}
    - side_effect: {0: a, 1: b, 2: c}
    expected_results:
    - keys:
      - 0
      values: 
      - 0
    - keys:
      - 0
      - 1
      values: 
      - 0
      - 1
    - keys:
      - 0
      - 1
      - 2
      values: 
      - a
      - b
      - c
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)
    
    # Result should be a lambda function
    assert type(result).__name__ == 'function'
    assert result.__name__ == '<lambda>'
    # Should return the expected value when key is passed to function
    for j in range(len(tests.expected_results)):
      keys = tests.expected_results[i]['keys']
      values = tests.expected_results[i]['values']
      for k in range(len(keys)):
        assert result(keys[k]) == values[k]


def test_case_bind_value() -> None:
  tests = '''
    test_description: Should return the value passed in 
      `get_side_effect_value_and_increment_count` as a lambda
    case_descriptions: return values for the function created
    cases:
    - data: 0
    - data: '1'
    - data: one
    expected_results:
    - 0
    - '1'
    - one
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)
    
    # Result should be a a value
    assert result == tests.expected_results[i]


def test_get_bind_object() -> None:
  tests = '''
    test_description: Should return a value of function patch depending on the 
      inputs into the function
    case_descriptions: 
    - returns a string
    - returns a integer
    - a side effect that returns value at the index of the number of times it
      has been called
    - a side effect that returns value associated with a key in a dictionary
    - function that returns a value when called
    cases:
    - value: value
      side_effect: null
    - value: 1
      side_effect: null
      return_value: null
    - value: null
      side_effect: [0, 1, 2, 3]
      return_value: null
    - value: null
      side_effect: {0: 0, 1: 1, 2: 2}
      return_value: null
    - value: null
      side_effect: null
      return_value:  return_value
    expected_results:
    - type: str
      name: str
    - type: int
      name: int
    - type: function
      name: <lambda>
    - type: function
      name: <lambda>
    - type: function
      name: <lambda>
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)

    if _case['value'] is not None:

      continue
    
    # Result should be the correct type/name
    assert result.__name__ == tests.expected_results[i]['name']
    assert type(result).__name__ == tests.expected_results[i]['type']


def test_case_parent_object_is_module() -> None:
  tests = '''
    test_description: Should return the attribute from a module
    case_descriptions: module and attribute name
    cases:
    - parent: {test_resources}
      object_name: add
    - parent: {test_resources}
      object_name: subtract
    - parent: {test_resources}
      object_name: foo
    - parent: {test_resources}
      object_name: function_does_exist_in_module_0
    expected_results:
    - name: add
      type: function
    - name: subtract
      type: function
    - name: foo
      type: function
    - name: add
      type: NoneType
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case['parent'] = test_resources

    # Execute function
    result = function(**_case)
    
    # Result should be the correct type and name
    assert type(result).__name__ == tests.expected_results[i]['type']
    if result is None:
      continue
    assert result.__name__ == tests.expected_results[i]['name']


def test_case_parent_object_is_dict() -> None:
  tests = '''
    test_description: Should return the value associated with a key in a
      dictionary
    case_descriptions: dictionary and key
    cases:
    - parent: {test_resources.dictionary_module}
      object_name: add
    - parent: {test_resources.dictionary_module}
      object_name: subtract
    - parent: {test_resources.dictionary_module}
      object_name: foo
    - parent: {test_resources.dictionary_module}
      object_name: function_does_exist_in_module_0
    expected_results:
    - name: add
      type: function
    - name: subtract
      type: function
    - name: foo
      type: function
    - name: add
      type: NoneType
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case['parent'] = test_resources.dictionary_module

    # Execute function
    result = function(**_case)
    
    # Result should be the correct type and name
    assert type(result).__name__ == tests.expected_results[i]['type']
    if result is None:
      continue
    assert result.__name__ == tests.expected_results[i]['name']


def test_case_parent_object_is_none() -> None:
  tests = '''
    test_description: Should return null when the parent object is null
    case_descriptions: parent object is null
    cases:
    - parent: null
      object_name: add
    - parent: null
      object_name: null
    expected_results:
    - value: null
      type: NoneType
    - value: null
      type: NoneType
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(**_case)
    
    # Result should be the correct type and name
    assert type(result).__name__ == tests.expected_results[i]['type']
    assert result == tests.expected_results[i]['value']


def test_get_object_hierarchy(get_locals) -> None:
  tests = '''
    test_description: Should return the object and its parent, the object it is 
      housed in, as a `ObjectHierarchy` object.
    case_descriptions: 
    cases:
    - object_name: test_resources
      _locals: _locals
    - object_name: test_resources.add
      _locals: _locals
    - object_name: test_resources.subtract
      _locals: _locals
    - object_name: test_resources.foo
      _locals: _locals
    - object_name: test_resources.dictionary_module.foo
      _locals: _locals
    - object_name: test_resources.dictionary_module.add
      _locals: _locals
    - object_name: test_resources.dictionary_module.subtract
      _locals: _locals
    - object_name: test_resources.variable_1
      _locals: _locals
    - object_name: test_resources.variable_2
      _locals: _locals
    - object_name: None.None
      _locals: _locals
    expected_results:
    - parent:
        _type: dict
        name: locals
      child:
        _type: module
        name: test_resources
    - parent:
        _type: module
        name: test_resources
      child:
        _type: function
        name: add
    - parent:
        _type: module
        name: test_resources
      child:
        _type: function
        name: subtract
    - parent:
        _type: module
        name: test_resources
      child:
        _type: function
        name: foo
    - parent:
        _type: dict
        name: dictionary_module
      child:
        _type: function
        name: foo
    - parent:
        _type: dict
        name: dictionary_module
      child:
        _type: function
        name: add
    - parent:
        _type: dict
        name: dictionary_module
      child:
        _type: function
        name: subtract
    - parent:
        _type: module
        name: test_resources
      child:
        _type: int
        name: variable_1
    - parent:
        _type: module
        name: test_resources
      child:
        _type: str
        name: variable_2
    - parent:
        _type: NoneType
        name: None
      child:
        _type: NoneType
        name: None
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  from test_resources import app as test_resources

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    # Restore locals at the end
    _case['_locals'] = get_locals
    
    # Execute function
    result = function(**_case)
    
    # Result should be the correct type
    assert type(result).__name__ == 'ObjectHierarchy'
    # Fields should have the correct values
    expected_parent = tests.expected_results[i]['parent']
    expected_child = tests.expected_results[i]['child']
    result.parent.name = expected_parent['name']
    result.parent._type = expected_parent['_type']
    result.child.name = expected_child['name']
    result.child._type = expected_child['_type']

    # Save as global variable for use in later tests
    global OBJECT_HIERARCHY
    OBJECT_HIERARCHY['original'].append(result)
    

def test_case_patch_when_parent_object_is_module() -> None:
  tests = '''
    test_description: Should bind an object to an attribute in a module and 
      return True, otherwise false
    case_descriptions: Set attributes to null if they exist
    cases:
    - parent_object: test_resources
      object_name: add
      bind_object: null
    - parent_object: test_resources
      object_name: foo
      bind_object: null
    - parent_object: test_resources
      object_name: attribute_does_not_exist
      bind_object: null
    expected_results:
    - True
    - True
    - False
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case['parent_object'] = test_resources

    # Execute function
    result = function(**_case)
    
    # Result should be a boolean
    assert type(result).__name__ == 'bool'
    assert result == tests.expected_results[i]


def test_case_patch_when_parent_object_is_dict() -> None:
  tests = '''
    test_description: Should bind an object to a key in a dictionary and return
      True, otherwise False
    case_descriptions: Set key's value to null if it exists
    cases:
    - parent_object: test_resources
      object_name: add
      bind_object: null
    - parent_object: test_resources
      object_name: subtract
      bind_object: null
    - parent_object: test_resources
      object_name: foo
      bind_object: null
    - parent_object: test_resources
      object_name: attribute_does_not_exist
      bind_object: null
    expected_results:
    - True
    - True
    - True
    - False
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    _case['parent_object'] = test_resources.dictionary_module

    # Execute function
    result = function(**_case)
    
    # Result should be a boolean
    assert type(result).__name__ == 'bool'
    assert result == tests.expected_results[i]


def test_patch_object() -> List[app.Object]:
  tests = '''
    test_description: Should patch an object and return True, otherwise False
    case_descriptions: Function with in a module and dictionary to patch
    cases:
    - object_name: test_resources.add
      bind_object: bind_object
      object_hierarchy: null
    - object_name: test_resources.foo
      bind_object: bind_object
      object_hierarchy: null
    - object_name: test_resources.subtract
      bind_object: bind_object
      object_hierarchy: null
    - object_name: test_resources.dictionary_module.add
      bind_object: bind_object
      object_hierarchy: null
    - object_name: test_resources.dictionary_module.foo
      bind_object: bind_object
      object_hierarchy: null
    - object_name: test_resources.dictionary_module.subtract
      bind_object: bind_object
      object_hierarchy: null
    - object_name: test_resources.dictionary_module.does_not_exist
      bind_object: bind_object
      object_hierarchy: null
    expected_results:
    - True
    - True
    - True
    - True
    - True
    - True
    - False
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  # Store object levels to use in the next test
  store = []

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]
    # Get object levels
    _case['object_hierarchy'] = app.get_object_hierarchy(
      object_name=_case['object_name'],
      _locals=globals(),
    )
    # Create a bind object and delete `object_name` from the dictionary
    _case['bind_object'] = lambda *x: _case['bind_object']
    del _case['object_name']

    # Execute function
    result = function(**_case)
    
    # Result should be a boolean
    assert type(result).__name__ == 'bool'
    # Should return True if patch was successful, false otherwise.
    assert result == tests.expected_results[i]


# def test_revert_patches() -> None:
#   tests = '''
#     test_description: Should try to revert patched objects back to their 
#       original functionality. If the revert was successful True is added to the 
#       store `data.reverted`, otherwise False is added. Should return a `Data` 
#       object
#     cases: 
#     - patched:
#       - True
#       - True
#       - True
#       - True
#       - True
#       - True
#       - False
#       object_hierarchy: object_hierarchy
#     expected_results:
#     - reverted: 
#       - True
#       - True
#       - True
#       - True
#       - True
#       - True
#       - null
#   '''
#   # set env vars
#   tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

#   # Load test cases into dataclass
#   tests = safe_load(tests)
#   tests = Tests(**tests)

#   # Get the function to test
#   data = get_function_to_test.Data(
#     test_function_name=get_function_to_test.get_test_function_name(), 
#     _module=app,
#   )
#   function = get_function_to_test.main(data=data)

#   for i in range(len(tests.cases)):
#     # Setup
#     _case = tests.cases[i]
#     # Get object levels
#     _case['object_hierarchy'] = OBJECT_HIERARCHY['original']

#     _case = dict(data=app.Data(**_case))

#     # Execute function
#     result = function(**_case)
    
#     # Result should be a `Data` object
#     assert type(result).__name__ == 'Data'
#     # Result should have the correct field values
#     for field, expected_value in tests.expected_results[i].items():
#       result_value = getattr(result, field)
#       assert result_value == expected_value


def format_parent_child_values(
  object_hierarchies: List[app.ObjectHierarchy],
) -> List[app.ObjectHierarchy]:
  ''''''
  n = len(object_hierarchies)
  for i in range(n):
    # object_hierarchies[i].parent.value = str(object_hierarchies[i].parent.value)
    # object_hierarchies[i].child.value = str(object_hierarchies[i].child.value)
    object_hierarchies[i].parent.value = None
    object_hierarchies[i].child.value = None
  return object_hierarchies


def test_main(get_locals) -> None:
  tests = '''
    test_description: Should patch an object and return True, otherwise False
    case_descriptions: Function with in a module and dictionary to patch
    cases:
    - data:
        patches:
        - object_name: test_resources.add
          return_value: add_patched
    - data:
        patches:
        - object_name: test_resources.subtract
          value: subtract_patched
    - data:
        patches:
        - object_name: test_resources.foo
          side_effect: 
          - foo_patched_0
          - foo_patched_1
    - data:
        patches:
        - object_name: test_resources.dictionary_module.add
          value: add_patched
    - data:
        patches:
        - object_name: test_resources.dictionary_module.subtract
          return_value: subtract_patched
    - data:
        patches:
        - object_name: test_resources.dictionary_module.foo
          side_effect: {0: 0, 1: 1}
    expected_results:
    - object_hierarchies:
      - child:
          _type: function
          name: add
          value: null
        parent:
          _type: module
          name: test_resources
          value: null
      patched:
      - true
      patches:
      - object_name: test_resources.add
        return_value: add_patched
        side_effect: null
        value: null
      reverted: []
    - object_hierarchies:
      - child:
          _type: function
          name: subtract
          value: null
        parent:
          _type: module
          name: test_resources
          value: null
      patched:
      - true
      patches:
      - object_name: test_resources.subtract
        return_value: null
        side_effect: null
        value: subtract_patched
      reverted: []
    - object_hierarchies:
      - child:
          _type: function
          name: foo
          value: null
        parent:
          _type: module
          name: test_resources
          value: null
      patched:
      - true
      patches:
      - object_name: test_resources.foo
        return_value: null
        side_effect:
        - foo_patched_0
        - foo_patched_1
        value: null
      reverted: []
    - object_hierarchies:
      - child:
          _type: function
          name: add
          value: null
        parent:
          _type: dict
          name: dictionary_module
          value: null
      patched:
      - true
      patches:
      - object_name: test_resources.dictionary_module.add
        return_value: null
        side_effect: null
        value: add_patched
      reverted: []
    - object_hierarchies:
      - child:
          _type: function
          name: subtract
          value: null
        parent:
          _type: dict
          name: dictionary_module
          value: null
      patched:
      - true
      patches:
      - object_name: test_resources.dictionary_module.subtract
        return_value: subtract_patched
        side_effect: null
        value: null
      reverted: []
    - object_hierarchies:
      - child:
          _type: function
          name: foo
          value: null
        parent:
          _type: dict
          name: dictionary_module
          value: null
      patched:
      - true
      patches:
      - object_name: test_resources.dictionary_module.foo
        return_value: null
        side_effect:
          0: 0
          1: 1
        value: null
      reverted: []
  '''
  # set env vars
  tests = tests.replace('{TEST_RESOURCES_DIR}', TEST_RESOURCES_DIR)

  # Load test cases into dataclass
  tests = safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)

  for i in range(len(tests.cases)):
    # Setup
    _case = tests.cases[i]

    # Execute function
    result = function(
      data=_case['data'],
      # revert=_case['revert'],
      _locals=get_locals,
    )

    # Result should be a `Data` object
    assert type(result).__name__ == 'Data'

    # Format results
    result.object_hierarchies = format_parent_child_values(
      object_hierarchies=result.object_hierarchies)
    # Result should have the correct field values
    assert asdict(result) == tests.expected_results[i]


if __name__ == '__main__':
  # Invoke pytest for this module
  pytest_arguments = sys.argv
  pytest_arguments.extend([
    # '-x', 
    '-s', 
    '--verbose', 
    '--cov', '.', 
    '--cov-report', 'term-missing',
  ])
  pytest.main()
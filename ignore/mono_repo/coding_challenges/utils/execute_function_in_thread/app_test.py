from time import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Callable
import sys
import pytest
import yaml
from threading import Thread

from shared.execute_function_in_thread import app
from shared.get_function_to_test import app as get_function_to_test
from test_resources import app as test_resources


@dataclass
class Tests:
  test_description: str | None = None
  case_descriptions: List[Dict[str, str]] | Dict[str, str] | None = None
  cases: List[Any] | Any | None = None
  expected_results: List[Any] | Any | None = None
  expected_fields: List[bool] | bool | None = None


# Global variable for storing and 
# accessing threads during tests
THREADS = []


def test_case_main_args_data_data() -> None:
  tests = '''
    test_description: Should return the value for the `data` key inside the
      `main_args` dictionary passed into the function
    case_descriptions:
    - key value is null
    - key value is a empty dictionary
    - key value is a nonempty dictionary
    - key value is a nonempty dictionary
    cases:
    - main_args:
        data: {}
    - main_args:
        data:
          target: null
          kwargs: null
          args: null
          threads: null
    expected_results:
    - target: null
      kwargs: null
      args: null
      threads: null
      store_name: STORE
    - target: null
      kwargs: null
      args: null
      threads: null
      store_name: STORE
  '''

  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
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
    _case['main_args']['data'] = app.Data(**_case['main_args']['data'])

    # Execute function
    result = function(**_case)
    
    # Result should be correct type
    assert type(result).__name__ == 'Data'
    # Result should have correct values
    result = asdict(result)
    assert result == tests.expected_results[i]


def test_case_main_args_data_dict() -> None:
  tests = '''
    test_description: Should return a Data object whose fields, values 
      correspond to the key, values from the main_args input
    case_descriptions: data is a dictionary with null values for keys
    cases:
    - main_args:
        data:
          target: null
          kwargs: null
          args: null
          threads: null
    expected_results:
    - target: null
      kwargs: null
      args: null
      threads: null
      store_name: STORE
  '''

  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
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
    
    # Result should be the correct type
    assert type(result).__name__ == 'Data'
    # Result should have the correct fields and values
    result = asdict(result)
    assert result == tests.expected_results[i]


def test_case_main_args_data_none() -> None:
  tests = '''
    test_description: Should return a Data object from the target, kwargs, 
      args, and threads keys of the main_args dictionary 
    case_descriptions: main_args keys are defined as null
    cases:
    - main_args:
        target: null
        kwargs: null
        args: null
        threads: null
    expected_results:
    - target: null
      kwargs: null
      args: null
      threads: null
      store_name: STORE
  '''

  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
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
    
    # Result should be of the correct type
    assert type(result).__name__ == 'Data'
    # Result should have the correct fields and values
    result = asdict(result)
    assert result == tests.expected_results[i]


def test_setup_data() -> None:
  tests = '''
    test_description: Should return a `Data` object from the arguments passed
      into the main function
    case_descriptions:
    - data value is an empty dictionary
    - data value is an dictionary with null values
    - data is null
    cases:
    - main_args:
        data: {}
    - main_args:
        data: 
          target: null
          kwargs: null
          args: null
          threads: null
    - main_args:
        data: null
        target: null
        kwargs: null
        args: null
        threads: null
    expected_results:
    - target: null
      kwargs: null
      args: null
      threads: null
      store_name: STORE
    - target: null
      kwargs: null
      args: null
      threads: null
      store_name: STORE
    - target: null
      kwargs: null
      args: null
      threads: null
      store_name: STORE
  '''

  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
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
    # Convert ith object to Dataclass
    if i == 1:
      _case['main_args']['data'] = app.Data(**_case['main_args']['data'])

    # Execute function
    result = function(**_case)

    # Result should be of the correct type
    assert type(result).__name__ == 'Data'
    # Result should have the correct fields and values
    result = asdict(result)
    assert result == tests.expected_results[i]


def test_convert_data_fields_to_lists() -> None:
  tests = '''
    test_description: Should format the dataclass by converting non-list field
      values to lists
    case_descriptions:
    - an empty dictionary
    - a dictionary with null values
    - a dictionary with empty values for lists
    cases:
    - data: {}
    - data: 
        target: null
        kwargs: null
        args: null
        threads: null
    - data: 
        target: null
        kwargs: []
        args: []
        threads: []
    expected_results:
    - target: null
      kwargs: []
      args: []
      threads: []
      store_name: STORE
    - target: null
      kwargs: []
      args: []
      threads: []
      store_name: STORE
    - target: null
      kwargs: []
      args: []
      threads: []
      store_name: STORE
  '''

  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
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
    # Convert dictionary to dataclass
    _case['data'] = app.Data(**_case['data'])

    # Execute function
    result = function(**_case)

    # Result should be of the correct type
    assert type(result).__name__ == 'Data'
    # Result should have the correct fields and values
    result = asdict(result)
    assert result == tests.expected_results[i]


def test_create_threads() -> None:
  tests = '''
    test_description: Should return a list of Threads created for a target 
      function and each of the function's args or kwargs. 
    case_descriptions:
    - target function with a single kwargs
    - target function with a single args
    - target function with a single kwargs and single args
    - target function with a two kwargs and two args
    cases:
    - data: 
        target: null
        kwargs: [{name: Earth_0}]
        args: []
        threads: []
    - data: 
        target: null
        kwargs: []
        args: [[World_0]]
        threads: []
    - data: 
        target: null
        kwargs: [{name: Earth_1}]
        args: [[World_1]] 
        threads: []
    - data: 
        target: null
        kwargs: [{name: World_1}, {name: Venus_1}]
        args: [[World_1], [Mars_1]] 
        threads: []
    expected_results:
    - - <Thread(Thread-1 (hello_world), initial)>
    - - <Thread(Thread-2 (hello_world), initial)>
    - - <Thread(Thread-3 (hello_world), initial)>
      - <Thread(Thread-4 (hello_world), initial)>
    - - <Thread(Thread-5 (hello_world), initial)>
      - <Thread(Thread-6 (hello_world), initial)>
      - <Thread(Thread-7 (hello_world), initial)>
      - <Thread(Thread-8 (hello_world), initial)>
  '''

  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
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
    # Convert dictionary to dataclass
    _case['data'] = app.Data(**_case['data'])
    _case['data'].target = test_resources.hello_world

    # Execute function
    results = function(**_case)

    # Results should be a list containing `Threads`
    assert type(results).__name__ == 'list'
    for j in range(len(results)):
      assert type(results[j]).__name__ == 'Thread'
      # Thread cast as a string should be correct
      assert str(results[j]) == tests.expected_results[i][j]

    # Store threads for use in succeeding tests, `test_start_threads`
    # global THREADS
    THREADS.extend(results)


def test_start_threads() -> None:
  tests = '''
    test_description: Should run each thread within a list of threads
    case_descriptions:
    - Threads stored in a global variable. Value set inside test.
    cases:
    - threads: null
    expected_results: True
  '''

  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
  tests = Tests(**tests)

  # Get the function to test
  data = get_function_to_test.Data(
    test_function_name=get_function_to_test.get_test_function_name(), 
    _module=app,
  )
  function = get_function_to_test.main(data=data)
  
  # Execute function 
  result = function(threads=THREADS)

  # Each thread should have been run and stopped 
  for thread in THREADS:
    # assert thread._is_stopped is True
    assert thread._is_stopped is True
  # Function should return True after each thread starts/finishes
  assert result == tests.expected_results


def test_get_store_from_targets_module() -> None:
  tests = '''
    test_description: Should return a global variable in the target function's
      module. The variable is used to return the results of executing the 
      target in multiple threads 
    case_descriptions:
    - Store exists in target's module
    - Store doesn't exist in target's module
    cases:
    - target: ${test_resources.hello_world}
      store_name: STORE
    - target: ${test_resources.hello_world}
      store_name: STORE_DOES_NOT_EXIST
    expected_results:
    - - Hello Earth_0
      - Hello World_0
      - Hello World_1
      - Hello Earth_1
      - Hello World_1
      - Hello Mars_1
      - Hello World_1
      - Hello Venus_1
    - []
  '''

  # Load test cases into dataclass
  tests = yaml.safe_load(tests)
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
    _case['target'] = test_resources.hello_world

    # Execute function
    results = function(**_case)

    # Result should be the correct type
    result_type = type(results).__name__
    expected_type = type(tests.expected_results[i]).__name__
    assert result_type == expected_type
    # Result should be the correct value
    # Sort incase threads finish non-sequentially
    results.sort()
    tests.expected_results[i].sort()
    assert results == tests.expected_results[i]



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
  
#! /usr/bin/env python3

from dataclasses import dataclass, asdict, fields, field
from typing import List, Dict, Any, Callable
from types import ModuleType
import yaml
import dacite
from os.path import dirname, basename, splitext, join
from os import listdir
from inspect import getmembers, isfunction
import ast

from app import cast_data_as
from app import patch_objects
from app.patch_objects import Patch
from app import get_module_at_path
from app import thread_function_executions
from app import error_handler
from app import get_function_definitions
from app import get_environment


STORE_RESULTS = []
EXCLUDE_FUNCTIONS = ['example']
ENV = get_environment.main(data=__file__)


@dataclass
class Data:
  values: List[Any] = field(default_factory=lambda: [])
  cast_as: List[str] = field(default_factory=lambda: [])
  file_path: str | None = None


@dataclass
class Coverage:
  tests_count: int = 0
  tests_passed_count: int = 0
  tests_passed_percent: float = 0


@dataclass
class Case:
  module_paths: List[str] = field(default_factory=lambda: [])
  function_name: str | None = None
  description: List[str] | str = ''
  patches: List[Patch] | Patch | None = None
  inputs: Data | None = None
  expected_outputs: List[Any] = field(default_factory=lambda: [])
  outputs: Data = field(default_factory=lambda: Data())
  assertions: List[str] = field(default_factory=lambda: [])
  results: List[List[bool]] = field(default_factory=lambda: [])
  coverage: Coverage = field(default_factory=lambda: Coverage())


@dataclass
class Test:
  yml_path: str | None = None
  module_path: str | None = None
  exclusions: List[str] | str = field(default_factory=lambda: EXCLUDE_FUNCTIONS)
  test_resources_dir_path: str | None = None
  test_resources_modules_paths: List[str] | None = None
  cases: List[Case] = field(default_factory=lambda: [])
  coverage: Dict[str, Coverage] = field(default_factory=lambda: {})


# @error_handler.main
def get_module_path_from_yml_path(
  yml_path: str,
  module_path: str,
) -> str:
  '''Returns the path to a python file associated with a yml file 
  if the path hasn't been set'''
  if module_path is not None:
    return module_path
  return yml_path.replace('.yml', '.py')


# @error_handler.main
def get_test_resources_dir_path(
  yml_path: str, 
  test_resources_dir_path: str,
) -> str:
  '''Returns the path to the test resources directory associated with a 
  python and yml file if the path hasn't already been set'''
  if test_resources_dir_path is not None:
    return test_resources_dir_path
  parent_dir = dirname(yml_path)
  return join(parent_dir, 'test_resources')


# @error_handler.main
def get_test_resources_modules_paths(
  test_resources_dir_path: str,
) -> List[str]:
  '''Returns a list of paths for modules within the test resources directory'''
  store = []
  files = listdir(test_resources_dir_path)
  for file in files:
    extension = splitext(file)[1]
    if extension != '.py':
      continue
    file_path = join(test_resources_dir_path, file)
    store.append(file_path)
  return store


# @error_handler.main
def get_module_from_path(module_paths: List[str]) -> Dict[str, ModuleType]:
  '''Returns a dictionary with keys being the name of modules and values
  being the the modules'''
  store = {}
  for module_path in module_paths:
    module = get_module_at_path.main(data=module_path)
    store[module.name] = module._object
  return store


# @error_handler.main
def format_cases_for_threading(test: Test) -> List[List[Case]]:
  '''Formats the test cases to facilitate threading downstream'''
  n = len(test.cases)
  for i in range(n):
    # Combine the paths module paths into a single list
    module_paths = test.test_resources_modules_paths + [test.module_path]    
    test.cases[i].module_paths = module_paths
    test.cases[i] = [test.cases[i]]
  return test.cases


# @error_handler.main
def cast_data(
  data: Data, 
  modules: Dict[str, ModuleType], 
) -> List[Any]:
  '''Returns a list of values cast to specified types'''
  # No casting needed
  if data.cast_as in [None, []]:
    return data.values

  # Store modules as list of `Module` dataclass objects
  modules_as_dataclasses = []
  for key, value in modules.items():
    if key == '__builtins__':
      key = 'standard_library'
    module = cast_data_as.Module(
      name=key,
      _object=value,
    )
    modules_as_dataclasses.append(module)
  # Setup and cast data
  data = cast_data_as.Data(
    values=data.values,
    constructors=data.cast_as,
    modules=modules_as_dataclasses,
  )
  return cast_data_as.main(data=data)


# @error_handler.main
def call_function_with_data(
  function: Callable, 
  inputs: List[Any | None],
) -> List[Any | None]: 
  '''Returns the results of calling the function to test with input data'''
  store = []
  n = len(inputs)
  for i in range(n):
    result = None
    try:
      result = function(**inputs[i])
    except:
      result = function(inputs[i])
    finally:
      store.append(result)
  return store


# @error_handler.main
def get_patched_objects(
  modules: Dict[str, ModuleType],
  patches: List[Patch] | None,
  _globals: Dict[str, Any] = globals(),
) -> None:
  '''Returns a dictionary containing modules, which have objects that
  have been patched'''
  if patches in [[], None]:
    return modules

  # Setup data and patch objects
  data = patch_object.Data(
    modules=modules,
    patches=patches,
  )
  return patch_object.main(data=data)


# @error_handler.main
def setup_assertions(
  n_output_values: int,
  assertions: List[str],
) -> List[str]:
  '''Returns a list of assertion functions to call to make to validate that 
  a functions output is as expected'''
  # Equal assertions if no assertions set
  if assertions in [[], None]:
    return ['equal' for i in range(n_output_values)]

  n = len(assertions)
  # Should be a 1 to many or 1 to 1 match 
  # between assertions and output values
  if n != n_output_values and n > 1:
    message = ''
    raise RuntimeError(message)
  # 1 to many match
  if n == 1:
    return [assertions[0] for i in range(n_output_values)]
  # 1 to 1 match
  if n == n_output_values:
    return assertions


# @error_handler.main
def assert_equal(
  output: Any, 
  expected_output: Any, 
  param: Any = None,
) -> bool:
  '''Returns true if the output equals the expected output'''
  if output == expected_output:
    return True
  return False


# @error_handler.main
def assert_greater_than(
  output: Any, 
  expected_output: Any, 
  param: Any = None,
) -> bool:
  '''Returns'''
  if output > expected_output:
    return True
  return False


# @error_handler.main
def assert_less_than(
  output: Any, 
  expected_output: Any, 
  param: Any = None,
) -> bool:
  ''''''
  if output < expected_output:
    return True
  return False


# @error_handler.main
def assert_has_values(
  output: Any, 
  expected_output: Any,
  param: Any = None,
) -> List[bool]:
  ''''''
  store = []
  if isinstance(output, dict):
    for key, expected_value in expected_output.items():
      value = output[key]
      result = value == expected_value
      store.append(result)

  if hasattr(output, '__dataclass_fields__'):
    for key, expected_value in expected_output.items():
      value = getattr()
      result = value == expected_value
      store.append(result)
  
  return store


ASSERTION_SWITCHER = {
  'str': lambda assertion: {assertion: assertion},
  'dict': lambda assertion: assertion,
}


# @error_handler.main
def get_assertion_result(
  output: Any, 
  expected_output: Any, 
  assertion: dict,
) -> Any:
  _type = type(assertion).__name__
  assertion_switcher = ASSERTION_SWITCHER[_type]
  assertion = assertion_switcher(assertion)
  key = list(assertion.keys())[0]
  function_name = f'assert_{key}'
  function = globals()[function_name]
  return function(output, expected_output, assertion[key])

  
# @error_handler.main
def verify_outputs_against_expected_outputs(
  outputs_values: List[Any],
  expected_outputs: List[Any],
  assertions: List[str | List[str]],
) -> List[bool]:
  store = []
  n = len(outputs_values)
  for i in range(n):
    assertion_result = get_assertion_result(
      output=outputs_values[i],
      expected_output=expected_outputs[i],
      assertion=assertions[i]
    )
    store.append(assertion_result)
  return store


# @error_handler.main
def get_case_coverage(
  coverage: Coverage, 
  results: List[bool],
) -> Coverage:
  n = 0
  store = []
  for result in results:
    n += 1
    if isinstance(result, list) is False:
      store.append(result)
      continue
    if False in result:
      result = False
    result = True
    store.append(result)

  tests_passed_count = sum(store)
  coverage.tests_count = n
  coverage.tests_passed_count = tests_passed_count
  coverage.tests_passed_percent = tests_passed_count / n * 100
  return coverage


# @error_handler.main
def run_test_case(case: Case) -> Case:
  # Get and format module data
  modules = {}
  for module_path in case.module_paths:
    module = get_module_at_path.main(data=module_path)
    module.name = module.name.replace('.', '_')
    modules[module.name] = module._object
  module_names = list(modules.keys())
  
  # Patch objects and add to global space
  patched_objects = get_patched_objects(
    modules=modules,
    patches=case.patches,
  )
  for key, value in patched_objects.items():
    globals()[key] = value
  
  # Get function to test
  module = globals()[module_names[-1]]
  function = getattr(module, case.function_name)

  # Case input data
  case.inputs.values = cast_data(data=case.inputs, modules=modules)
  # Get function output data
  case.outputs.values = call_function_with_data(
    function=function,
    inputs=case.inputs.values,
  )

  # Cast output data
  case.outputs.values = cast_data(
    data=case.outputs, 
    modules=modules,
  )
  
  # Setup assertions
  case.assertions = setup_assertions(
    assertions=case.assertions,
    n_output_values=len(case.outputs.values),
  )
  # Compare outputs to expected
  case.results = verify_outputs_against_expected_outputs(
    outputs_values=case.outputs.values,
    expected_outputs=case.expected_outputs,
    assertions=case.assertions,
  )

  # Get the functions coverage
  case.coverage = get_case_coverage(
    coverage=case.coverage, 
    results=case.results,
  )
  

  return


# @error_handler.main
def get_list_of_user_defined_functions_from_module(module_path: str) -> List[str]:
  '''Returns a list a the user defined functions within a module'''
  # https://stackoverflow.com/questions/139180/how-to-list-all-functions-in-a-module
  source = None
  with open(module_path, 'r') as file:
    source = file.read()
  store = []
  for function in ast.parse(source).body:
    if not isinstance(function, ast.FunctionDef):
      continue
    store.append(function.name)
  return store


def setup_coverage_data(
  function_names: List[str],
  exclusions: List[str],
) -> Dict[str, Coverage]:
  store = {}
  for name in function_names:
    include = True

    for exclusion in exclusions:
      if name.find(exclusion) != -1:
        include = False
        break

    if include is True:
      store[name] = Coverage()
      
  return store
  
  
def get_coverage_for_functions(test: Test) -> Dict[str, Coverage]:
  total = Coverage()
  for case in test.cases:
    case = case[0]
    function_coverage = test.coverage[case.function_name]

    print(case.results)

    function_coverage.tests_count += len(case.results)
    function_coverage.tests_passed += sum(case.results)
    total.tests_count += len(case.results)
    total.tests_passed += sum(case.results)
    function_coverage.tests_coverage = function_coverage.tests_passed / function_coverage.tests_count
    function_coverage = test.coverage[case.function_name]

  test.coverage['total'] = total
  return test.coverage


def get_percent(part: float | int, whole: float | int) -> float:
  if whole == 0:
    return 0
  return part / whole * 100


def aggregate_function_coverages(
  cases: List[Case], 
  total_coverage: Dict,
) -> Dict[str, Coverage]:
  for case in cases:
    case = case[0]
    coverage = total_coverage[case.function_name]
    coverage.tests_count += case.coverage.tests_count
    coverage.tests_passed_count += case.coverage.tests_passed_count
    coverage.tests_passed_percent = get_percent(
      part=coverage.tests_passed_count,
      whole=coverage.tests_count,
    )
  return total_coverage


def get_total_coverage(coverage: Dict[str, Coverage]) -> Dict[str, Coverage]:
  total_coverage = Coverage()
  total_percent = 0
  n = len(coverage)
  for key, value in coverage.items():
    total_percent += value.tests_passed_percent
  total_coverage.tests_passed_percent = total_percent / n
  coverage['total'] = total_coverage
  return coverage


def get_coverage(
  cases: List[Case], 
  module_path: str,
  exclusions: List[str],
) -> Coverage:
  function_names = get_function_definitions.main(
    module_path=module_path,
    output_attributes=['name'],
  )
  function_names = function_names['name']

  coverage = setup_coverage_data(
    function_names=function_names,
    exclusions=exclusions,
  )
  coverage = aggregate_function_coverages(
    cases=cases, 
    total_coverage=coverage,
  )
  coverage = get_total_coverage(coverage=coverage)
  return coverage


# @error_handler.main
def format_test(test: Test) -> Test:
  ''''''

  m = len(test.cases)
  for i in range(m):
    # n = len(test.cases[i])
    # for j in range(n):

    #   # Remove the modules paths as this is 
    #   # stored in the Test (main) dataclass
    #   # test.cases[i][j].module_paths = None

    #   l = len(test.cases[i][j].outputs.values)
    #   for k in range(l):

    #     pass
      
    # Cases outputs as a list within a list
    # Convert it to a single item
    test.cases[i] = test.cases[i][0]

    # Convert inputs and outputs to strings
    # TODO: May be a better way to make sure inputs/outputs are json 
    # serializeable
    # n = len(test.cases[i].outputs.values)
    # for k in range(n):
    #   test.cases[i].outputs.values[k] = str(
    #     test.cases[i].outputs.values[k])
    #   test.cases[i].inputs.values[k] = str(
    #     test.cases[i].inputs.values[k])

    # Convert dataclass to dictionary
    test.cases[i] = asdict(test.cases[i])

    # Remove the modules paths as this is 
    # stored in the Test (main) dataclass
    del test.cases[i]['module_paths']
  
  test = asdict(test)
  # Remove resources directory path
  del test['test_resources_dir_path']
  return test


SETUP_TEST_DATA_SWITCHER = {
  'Test': lambda test: test,
  'dict': lambda test: dacite.from_dict(Test, test),
}


def setup_test_data(test: Test) -> Test:
  # Convert input to Test dataclass
  test_type = type(test).__name__
  switcher = SETUP_TEST_DATA_SWITCHER[test_type]
  test = switcher(test=test)

  # Add the exclusion string to a list
  if isinstance(test.exclusions, str):
    test.exclusion = [test.exclusions]

  return test


# @error_handler.main
def main(test: Test | dict) -> Test:
  test = setup_test_data(test=test)

  test.module_path = get_module_path_from_yml_path(
    yml_path=test.yml_path,
    module_path=test.module_path,
  )
  test.test_resources_dir_path = get_test_resources_dir_path(
    yml_path=test.yml_path, 
    test_resources_dir_path=test.test_resources_dir_path,
  )
  test.test_resources_modules_paths = get_test_resources_modules_paths(
    test_resources_dir_path=test.test_resources_dir_path)

  cases = format_cases_for_threading(test=test)
  thread_function_executions.main(
    target=run_test_case,
    args=cases,
    store_name='STORE_RESULTS',
  )
  test.coverage = get_coverage(
    module_path=test.module_path,
    cases=test.cases,
    exclusions=test.exclusions,
  )

  test = format_test(test=test)
  return test


# @error_handler.main
def format_terminal_output(test: str) -> str:
  function_name_index = test.find('function_name')
  new_line_index = test[function_name_index:].find('\n') + function_name_index
  string = test[function_name_index:new_line_index]
  formatted_string = '\033[1m' + '\033[33m' + string + '\033[0m'
  test = test.replace(string, formatted_string)

  return test


# Test data for functions
test = '''
  yml_path: /home/femij/mono_repo/coding_challenges/utils/untested_test_cases/test_resources/arithmetic.yml
  test_resources_dir_path: /home/femij/mono_repo/coding_challenges/utils/untested_test_cases/test_resources
  cases:
  - function_name: add
    description: Should add two numbers and return the result
    inputs:
      values:
      - a: 0
        b: 0
      - a: 1
        b: 1
      cast_as:
      - Data
    expected_outputs: 
    - Data(a=0, b=0, result=0)
    - Data(a=1, b=1, result=2)
    outputs:
      cast_as:
      - str
    assertions: [] 
  - function_name: add
    description: Should add two numbers and return the result
    patches:
    - object_name: __builtins__.input
      return_value: '__builtins__.input_patched'
    inputs:
      values:
      - a: 0
        b: 0
      - a: 1
        b: 1
      cast_as:
      - Data
    expected_outputs:
    - a: 0
      b: 0
      result: 0
    - a: 1
      b: 1
      result: 2
    outputs:
      cast_as:
      - dict
    assertions: 
    - has_values    
  - function_name: add
    description: Should add two numbers and return the result
    patches: 
    - object_name: test_resources_arithmetic.add
      return_value: 'test_resources_arithmetic.add_patched'
    inputs:
      values:
      - a: 0
        b: 0
      - a: 1
        b: 1
      cast_as: 
      - Data
    expected_outputs:
    - test_resources_arithmetic.add_patched
    - test_resources_arithmetic.add_patched
    outputs:
      cast_as:
      - str
    assertions: [equal] 
'''
test = yaml.safe_load(test)
test = dacite.from_dict(Test, test)
test = main(test=test)
test = dict(test=test)
test_yml = yaml.dump(
  test, 
  indent=2, 
  sort_keys=False,
  default_flow_style=False,
)

test_yml = format_terminal_output(test=test_yml)
print(test_yml)


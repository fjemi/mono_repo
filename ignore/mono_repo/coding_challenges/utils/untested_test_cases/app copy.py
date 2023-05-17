#! /usr/bin/env python3

from dataclasses import dataclass, asdict, fields
from typing import List, Dict, Any, Callable
import yaml
import dacite
from os.path import dirname, basename, splitext, join
from os import listdir

from shared.cast_data_as import app as cast_data_as
from shared.patch_object import app as patch_object
from shared.get_module_at_path import app as get_module_at_path
from shared.execute_function_in_thread import app as execute_function_in_thread


@dataclass(slots=True)
class Case:
  function_name: str | None = None
  function: Callable | None = None
  description: str | None = None
  # test_resources: List[str] | str | None = None
  patch: List[dict] | dict | None = None
  input_data_cast_to: List[dict] | dict | None = None
  input_data: List[Any] | Any | None = None
  input_data_from_file: List[str] | str | None = None
  output_data: List[Any] | None = None
  output_data_cast_to: List[dict] | dict | None = None
  expected_data: List[Any] | Any | None = None
  expected_data_from_file: List[str] | str | None = None
  expected_data_cast_to: List[dict] | dict | None = None
  assertion: List[str] | str | None = None


@dataclass(slots=True)
class Tests:
  cases: List[Case] | Case | None = None
  module_path: str | None = None
  _module: ModuleType | None = None
  test_resources_path: str | None = None
  test_resources_module_paths: List[str] | str | None = None
  test_resources_modules: Dict[str, ModuleType] | None = None
  environment_variables: Dict | None = None


def case_setup_data_dict(data: Dict) -> Tests:
  return dacite.from_dict(Tests, data)


def case_setup_data_list(data: List) -> Tests:
  cases = []
  n = len(data)
  for i in range(n):
    cases.append(Case(**data[i]))
  return Tests(cases=cases)


def case_setup_data_str(data: str, _locals: Dict = locals()) -> Tests:
  data = yaml.safe_load(data)
  data_type = type(data).__name__
  function = f'case_setup_data_{data_type}'
  function = _locals[function]
  return function(data=data)


SETUP_DATA = {
  'NoneType': lambda data: Tests(),
  'str': case_setup_data_str,
  'dict': case_setup_data_dict,
  'list': case_setup_data_list,
}


def setup_main_data(data: str | Dict | Tests | None) -> Tests:
  data_type = type(data).__name__
  function = SETUP_DATA[data_type]
  return function(data=data)


def get_test_resources_path(
  module_path: str, 
  test_resources_path: str = None,
) -> str:
  # Path is already set
  if test_resources_path is not None:
    return test_resources_path
  # Set path from the module path
  file_name = basename(module_path)
  test_resources_path = module_path.replace(file_name, 'test_resources')
  return test_resources_path


def get_test_resources_module_paths(test_resources_path: str) -> List[str]:
  store = []
  # Get `.py` files from test resources directory
  files = listdir(test_resources_path)
  for _file in files:
    extension = splitext(_file)[-1]
    if extension == '.py':
      # file_name = basename(_file)
      # store.append(file_name)
      _file = join(test_resources_path, _file)
      store.append(_file)
  return store


def import_test_resources_modules_from_path(data: List[str]) -> Dict:
  store = {}
  for path in data:
    _module = get_module_at_path.main(data=path)
    store[_module.name] = _module._object
  return store


def import_functions_from_module(data: Tests) -> Tests:
  n = len(data.cases)
  for i in range(n):
    function = getattr(
      data._module._object, 
      data.cases[i].function_name,
    ) 
    data.cases[i].function = function
  return data


def cast_input_data(data: Tests) -> Tests:
  n = len(data.cases)
  for i in range(n):
    if data.cases[i].input_data_cast_to is None:
      continue

    data.cases[i].input_data = cast_data_as.main(
      dict(
        values=data.cases[i].input_data,
        constructors=data.cases[i].input_data_cast_to,
        modules=dict(path=data.module_path),
      )
    )
  return data


UNPACK_LAMBDA = {
  0: lambda function, input_data: function(**input_data),
  1: lambda function, input_data: function(*input_data),
  2: lambda function, input_data: function(*input_data),
  3: lambda function, input_data: function(input_data),
  4: lambda function, input_data: function(input_data),
}


def type_conditions(data: Any) -> str:
  data_type = type(data).__name__
  conditions = [
    data_type == 'dict',
    data_type == 'list',
    data_type == 'tuple',
    hasattr(data, '__dataclass_fields__') is True,
    data_type not in ['dict', 'list', 'tuple'] and hasattr(
      data, '__dataclass_fields__') is False,
  ]
  return conditions.index(1)



def execute_function_with_input_data(
  function: Callable, 
  input_data: List[Any],
) -> List[Any]:
  store = []
  n = len(input_data)
  for i in range(n):
    _case = type_conditions(input_data[i])
    unpack_lambda = UNPACK_LAMBDA[_case]
    result = unpack_lambda(
      function=function,
      input_data=input_data[i],
    )
    store.append(result)
  return store

    # exceptions = []

    # # Execute function with data
    # try:
    #   result = function(input_data[i])
    # except Exception as e:
    #   exceptions.append[e]
    # finally:
    #   store.append(result)
    #   continue

    
    # # Execute function with data unpacked
    # try:
    #   result = unpack_lambda(
    #     function=function,
    #     input_data=input_data[i],
    #   )
    # except Exception as e:
    #   exceptions.append[e]
    # finally:
    #   store.append(result)
    #   continue

    # # Throw exception if function can not be executed
    # # with packed or unpacked data
    # message = f'{exceptions}'
    # raise RuntimeError(message)

  # return store



def main(data: Tests | Dict | None) -> Tests:
  # Setup
  data = setup_main_data(data=data)

  # Import the module to test
  data._module = get_module_at_path.main(data=data.module_path)
  
  # Import any modules from test resources
  data.test_resources_path = get_test_resources_path(
    module_path=data.module_path,
    test_resources_path=data.test_resources_path,
    )
  data.test_resources_module_paths = get_test_resources_module_paths(
    test_resources_path=data.test_resources_path)
  data.test_resources_modules = import_test_resources_modules_from_path(
    data=data.test_resources_module_paths,
  )
  

  # Add modules to global space
  # App to test
  globals()[data._module.name] = data._module._object
  # Test resources
  for key, value in data.test_resources_modules.items():
    globals()[key.replace('.', '_')] = value

  
  print(test_resources_arithmetic)

  
  # THREADED
  # Get function to test
  data = import_functions_from_module(data=data)

  # Cast input data
  data = cast_input_data(data=data)

  # Execute test cases
  n = len(data.cases)
  for i in range(n):
    # Patch objects
    patch_data = dict(patches=data.cases[i].patch)
    # patched_objects = patch_object.main(data=patch_data, _locals=locals())
    patched_objects = patch_object.main(data=patch_data)
    # print(dir(patched_objects))
    # print(patched_objects.object_hierarchies[-1].parent.value.keys())
    # test = patched_objects.object_hierarchies[-1].parent.value['__builtins__']
    # print(test['input']())


    # if data.cases[i].patch is None:
    #   data.cases[i].patch = []
    # for patch in data.cases[i].patch:
    #   patched_object = patch_object.main(data=patch, _locals=locals())
    #   print(patched_object)

    # Execute functions with input data
    function = data.cases[i].function
    input_data = data.cases[i].input_data
    results = execute_function_with_input_data(
      function=function,
      input_data=input_data,
    )
    data.cases[i].output_data = results

  # print(data.cases)
  # print(data._module)
  # Pre-processing: imports, casting, etc
  # data.data = cast_data_as.main(
  #   values=data.cases.data,
  #   constructors=data.cases.cast_data_as,
  #   modules=[
  #     dict(path=data.module_path),
  #   ]
  # )
  
  

  data.cases = format_cases(data=data.cases)
  data.cases = process_test_cases(data=data.cases)


  return data


FORMAT_CASE = {
  'NoneType': lambda data: [],
  'list': lambda data: data,
  'Case': lambda data: [data],
  'dict': lambda data: Case(**data),
  'str': lambda data: [data],
}


def format_cases(data: List[Case]) -> List[Case]:
  exclude_field = ['description', 'function', 'function_name']
  n = len(data)
  for i in range(n):
    for field in fields(data[i]):
      if field.name in exclude_field:
        continue
      value = getattr(data[i], field.name)
      value_type = type(value).__name__
      function = FORMAT_CASE[value_type]
      value = function(data=value)
      setattr(data[i], field.name, value)
  return data


def pre_process_test_case(data: Case) -> Case:
  # module = get_module_at_path.main(data.)
  # Load module to test
  # Load any test resources
  # get function
  # patch objects
  # Cast data

  return data


def execute_test_case(data: Case) -> Case:

  return data


def post_process_test_case(data: Case) -> Case:

  return data


def process_test_cases(data: List[Case]) -> List[Case]:
  # Process tests
  n = len(data)
  for i in range(n):
    _case = data[i]
    _case = pre_process_test_case(data=_case)
    _case = execute_test_case(data=_case)
    _case = post_process_test_case(data=_case)
    data[i] = _case
  return data





def example() -> None:
  import json
  import yaml


  data = f'''
    module_path: {__file__}
    cases:
    - description: null
      input_data: null
      expected_data: null
    - description: null
      input_data: null
      expected_data: null
    - description: null
      input_data: null
      expected_data: null
  '''
  data = main(data=data)
  print(data)


def example_patch_object_test() -> None:
  # data = '''
  #   module_path: /home/femij/mono_repo/coding_challenges/utils/untested_test_cases/test_resources/arithmetic.py
  #   cases:
  #   - function_name: add
  #     description: 
  #     input_data:
  #     - a: 0
  #       b: 0
  #     - a: 1
  #       b: 1
  #     input_data_cast_to:
  #     - Data
  #     expected_data:
  #     - a: 0
  #       b: 0
  #       result: 0
  #     - a: 1
  #       b: 1
  #       result: 2
  #     expected_data_cast_to:
  #     - Data
  #     # output_data:
  #     # output_data_cast_to:
  #     - dict
  #     assertion: null
  #   # passed:
  #   # failed:
  # '''


  data = '''
    module_path: /home/femij/mono_repo/coding_challenges/utils/untested_test_cases/test_resources/arithmetic.py
    test_resources_path: /home/femij/mono_repo/coding_challenges/utils/untested_test_cases/test_resources
    cases:
    - function_name: use_add
      description: Should add two numbers and return the result
      patch: 
      - object_name: input
        return_value: 'add_patched'
      input_data:
      - a: 0
        b: 0
      - a: 1
        b: 1
      expected_data:
      assertion: []     
    - function_name: add
      description: Should add two numbers and return the result
      patch: 
      - object_name: add
        return_value: 'add_patched'
      input_data_cast_to: 
      - name: Data
      input_data:
      - a: 0
        b: 0
      - a: 1
        b: 1
      expected_data:
      assertion: [] 
  '''

  # data = '''
  #   module_path: /home/femij/mono_repo/coding_challenges/utils/patch_object/app.py
  #   cases:
  #   - function_name: setup_data
  #     description: Returns an instance of the module's `Data` object from a
  #       dictionary.
  #     patch:
  #     - name: test_resources.app.add
  #       return_value: test_resources.app.add_patched
  #     input_data:
  #     - data: {}
  #     - object_hierarchies: null
  #       patches: 
  #       - function_name: function_name
  #         return_value: return_value
  #       patched: null
  #       reverted: null
  #     expected_data:
  #     - object_hierarchies: []
  #       patches: []
  #       patched: []
  #       reverted: []
  #     - object_hierarchies: [object_hierarchies]
  #       patches: [patched]
  #       patched: [patched]
  #       reverted: [reverted]
  #     assertion: [] 
  #   - function_name: setup_data
  #     description: Returns the `Data` object passed into the function
  #       `Data` object.
  #     input_data_cast_to:
  #     - name: Data
  #     input_data:
  #     - {}
  #     expected_data:
  #     - object_hierarchies: []
  #       patches: []
  #       patched: []
  #       reverted: []
  #     assertion: []
  # '''
  
  data = main(data=data)
  # print(data)

  n = len(data.cases)
  for i in range(n):
    data.cases[i].function = None
    data.cases[i] = asdict(data.cases[i])
    # print(json.dumps(data.cases[i], indent=2), '\n\n')
    cases = dict(case=data.cases[i])
    print(yaml.dump(cases, indent=2), '')




if __name__ == '__main__':
  # example()
  example_patch_object_test()


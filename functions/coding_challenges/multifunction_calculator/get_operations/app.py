from dataclasses import dataclass, field
from typing import Dict, List, Callable
from os import path, walk
from importlib.machinery import SourceFileLoader


@dataclass
class DataClass:
  '''
  description:
    Type hint representing a generic data class instance
  '''
  pass


@dataclass
class Operation:
  '''
  description:
    Represents a single operation (add, substract, etc) for a calculator
  attributes:
    - name:  Function needed to perform the operation
    - data: The data used as input for the function
  '''
  function: Callable
  data: DataClass


@dataclass
class Data:
  '''
  description:
    Represents the data needed to get the operations for the calculator
  attributes:
    - file_path: Path to a file, usually `app.py` in the root directory, used
        to locate the operations directory
    - operations_directory_name: The name of the directory containing the 
        operations
    - directory: The path to the operations directory
    - modules_path: A list of paths to the modules in the operations directory
    - operations: A dictionary of operation functions and data
  '''
  file_path: str 
  operations_directory_name: str = 'opertions'
  parent_directory: str | None = None
  operations_directory_path: str | None = None
  module_paths: List[str] = field(default_factory=lambda: [])
  operations: Dict[str, Operation] = field(default_factory=lambda: {})


def get_parent_directory(data: Data) -> str:
  '''
  description:
    Returns the parent directory for a given file's path
  '''
  return path.dirname(data.file_path)


def get_operations_directory_path(data: Data) -> str:
  '''
  description:
    Returns the path to the directory with the modules containing operations
    for the calculator
  '''
  return path.join(data.parent_directory, data.operations_directory_name)


def get_module_paths(data: Data) -> List[str]:
  '''
  description:
    Returns a list of python files; files must have the name
    `app.py`
  '''
  store = []
  for item in walk(data.operations_directory_path):
    file_directory = item[0]
    files = item[2]

    for file_name in files:
      condition = file_name == 'app.py'
      if condition is False:
        continue
      file_path = path.join(file_directory, file_name)
      store.append(file_path)
  return store


def get_operations_from_paths(data: Data) -> Dict[str, Operation]:
  '''
  description:
    Returns a dictionary with keys being the name of operations and
    the values containing the operation's functions and data
  '''
  functions = {}
  # Get the operations and data form each module at a given path
  for module_path in data.module_paths:
    # Load the modules named `app.py` given path
    module = SourceFileLoader('app', module_path).load_module()
    # Get functions that start with `calculate_` and the functions inputs
    for attribute in dir(module):
      condition = attribute.find('calculate_') > -1
      if condition is False:
        continue
      # Set function name and input; function_name = module.function
      operations_directory_name = path.dirname(module_path)
      folder_name = path.basename(operations_directory_name)
      key = f'{folder_name}.{attribute}'
      function = getattr(module, attribute)
      # Function inputes will be a dataclass defined as `Data`
      data = getattr(module, 'Data')
      functions[key] = Operation(function=function, data=data)
  return functions


def main(data: Data | dict | str) -> Data:
  '''Orchestration function that executes the function within this module'''
  data = type_handler.main(data=data, data_class=Data)
  data.parent_directory = get_parent_directory(data=data)
  data.operations_directory_path = get_operations_directory_path(data=data)
  data.module_paths = get_module_paths(data=data)
  data.operations = get_operations_from_paths(data=data)
  return data.operations


# file_path = '/home/femij/mono_repo/functions/coding_challenges/coding_challenges/multifunction_calculator/1_app.py'
# data = Data(file_path=file_path, operations_directory_name='operations')
# data = main(data)
# print(data)

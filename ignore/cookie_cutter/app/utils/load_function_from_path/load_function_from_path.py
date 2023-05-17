#!/usr/bin/env python3

from os.path import exists
import importlib.util
from dataclasses import dataclass, asdict
from typing import Union, Any, Callable


@dataclass
class Data:
  '''
  Summary
    Store data needed to import functions from a Python module
    given the path to the module
  Attributes
    module_path: Absolute path to a Python module
    module_name: The name of a Python module
    function_name: The name of a function a Python module. If blank, `module_name` is used.
  '''
  functions_dir: str = 'functions'
  module_name: str = 'hello_world'
  function_name: str = 'hello_world' 
  function: str = 'hello_world' 


def load_function_from_path(data: Union[Data, dict]) -> Callable:
  '''
  Summary
    Loads a function from a module given the absolute path to module.
  Paramters
    module_path: Absolute path to a Python module
    module_name: The name of a Python module
    function_name: The name of a function a Python module
  Returns
  '''

  if isinstance(data, dict):
    data = Data(**data)

  # Set path to the module containing the function
  path = f'{data.functions_dir}/{data.module_name}/{data.module_name}.py'
  # Handle non-existant module path
  if exists(path) is False:
    return None

  # Import module from path
  spec = importlib.util.spec_from_file_location(data.module_name, path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  # Function and module share the same name. No function name passed
  if data.function_name is None:
    data.function_name = data.module_name
  # Get function from module
  function = getattr(module, data.function_name)
  return function


def load_function_from_path_test():
  # Should 
  function = load_function_from_path(data=Data())
  result = function()
  print(result)
  assert asdict(result) == {'hello': 'world'}


if __name__ == '__main__':
  load_function_from_path_test()
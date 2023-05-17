from types import ModuleType
from typing import Callable
import inspect
from dataclasses import dataclass

from app import get_module_and_yml_paths

@dataclass
class Data:
  test_function_name: str = None
  _module: ModuleType = None
  prefix: str = 'test_'
  suffix: str = '_test'
  function_name: str = None
  function: Callable = None



def get_test_function_name(data: None = None) -> str:
  '''Returns the name of the function this function is called in.'''
  return inspect.stack()[1][3]


def get_function_name_from_test_function_name(
  test_function_name: str,
  prefix: str = None,
  suffix: str = None,
) -> str:
  '''Returns the function function being tested using the name of the test
  function.'''
  
  if prefix and test_function_name.find(prefix) != -1:
    m = len(prefix)
    return test_function_name[m:]
  
  if suffix and test_function_name.find(suffix) != -1:
    m = len(suffix)
    n = len(test_function_name)
    return test_function_name[:n - m]


def get_function_from_module(
  _module: ModuleType, 
  function_name: str,
) -> Callable:
  '''Returns a function from a module if the function is an attribute of the 
  module'''
  if hasattr(_module, str(function_name)) is True:
    return getattr(_module, str(function_name))


SETUP_MAIN_DATA = {
  'dict': lambda data: Data(**data),
  'Data': lambda data: data,
}


def setup_main_data(data: Data | dict) -> Data:
  cases = {
    isinstance(data, dict): 'dict',
    hasattr(data, '__dataclass_fields__'): 'Data',
  }
  _case = cases[1]
  function = SETUP_MAIN_DATA[_case]
  return function(data=data)


def main(data: Data | dict) -> Callable:
  data = setup_main_data(data=data)
  data.function_name = get_function_name_from_test_function_name(
    prefix=data.prefix,
    suffix=data.suffix,
    test_function_name=data.test_function_name,
  )
  return get_function_from_module(
    _module=data._module, 
    function_name=data.function_name,
  )


def example_add() -> None:
  from test_resources import app


  data = Data(
    test_function_name=get_test_function_name(), 
    _module=get_module_and_yml_paths, 
    prefix='example_',
  )
  function = main(data=data)
  print(function.__name__)


if __name__ == '__main__':
  example_add()
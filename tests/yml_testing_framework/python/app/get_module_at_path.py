from importlib.machinery import SourceFileLoader
from types import ModuleType
from typing import Dict, Any, List
import dataclasses as dc
from os.path import exists, dirname, basename, splitext
import types


@dc.dataclass
class Module:
  name: str | None = None
  path: str | None = None
  _object: ModuleType | None = None


def case_setup_str_data(data: str) -> Module:
  '''Setup data for cases where a string is passed into the main function'''
  return Module(path=data)


def case_setup_dict_data(data: Dict) -> Module:
  '''Setup data for cases where a dictionary is passed into the main function'''
  return Module(**data)


def case_setup_module_data(data: Module) -> Module:
  '''Setup data for cases where a `Module` object is passed into the main 
  function'''
  return data


def case_setup_nonetype_data(data: None) -> Module:
  '''Setup data for cases where a `None` value is passes into the main 
  function'''
  return Module()


def setup_data(data: Module | str | Dict, _locals: Dict = locals()) -> Module:
  '''Setups data passed into the main function of this module to facilitate
  processing downstream'''
  _case = type(data).__name__
  function_name = f'case_setup_{_case}_data'.lower()
  return _locals[function_name](data)


def case_path_exists_is_true(data: Module) -> ModuleType:
  '''Returns a python module at a given file path'''
  # TODO: 
  # https://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3
  # loader = SourceFileLoader(
  #   data.name, 
  #   data.path,
  # )
  # mod = types.ModuleType(loader.name)
  # loader.exec_module(mod)
  # return mod
  return SourceFileLoader(
    data.name, 
    data.path,
  ).load_module()


def case_path_exists_is_false(data: Module) -> None:
  '''Return `None` when a given file path doesn't exist'''
  return None


def case_name_is_none_is_false(name: str, path: str = None) -> str:
  '''Returns the `name` string passed in.'''
  return name


def case_name_is_none_is_true(path: str, name: None = None) -> str:
  '''Returns a string in the format `[module_name].[folder_name]`.'''
  # Get the folder name
  folder_name = dirname(path)
  folder_name = basename(folder_name)
  # Get the file name
  file_name = basename(path)
  file_name = splitext(file_name)[0]
  return f'{folder_name}.{file_name}'


def main(data: Module | str | Dict, _locals: Dict = locals()) -> Module:
  # Format data for processing downstream
  data = setup_data(data=data, _locals=_locals)

  # Set the module name
  _case = data.name is None
  function_name = f'case_name_is_none_is_{_case}'.lower()
  function = _locals[function_name]
  data.name = function(path=data.path, name=data.name)

  # Return module if it exists at path, otherwise null
  data.path = str(data.path)
  _case = exists(data.path)
  function_name = f'case_path_exists_is_{_case}'.lower()
  function = _locals[function_name]
  data._object = function(data)
  return data


def example() -> None:
  from time import time


  path = __file__.replace('app.py', 'test_resources/app.py')
  start = time()
  data = main(data={'path': path})
  end = time() - start


if __name__ == '__main__':
  example()
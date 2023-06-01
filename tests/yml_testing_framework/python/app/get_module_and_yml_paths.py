#!/usr/bin/env python3

import dataclasses as dc
from os.path import exists, splitext
from typing import List, Any, Dict
import dacite


@dc.dataclass
class Data:
  py_path: str | None = None
  yml_path: str | None = None


def get_file_extension(data: str) -> str:
  '''Returns the extension for a file'''
  return splitext(data)[1]


def case_setup_data_for_str(data: str) -> Data:
  '''Returns a dataclass when a string is passed into the main function. 
  Determines which field. Determines which field to set string to based on
  the string/paths extension'''
  extension = get_file_extension(data=data)
  extension_mapper = {'.py': 'py_path', '.yml': 'yml_path', '.yaml': 'yml_path'}
  field = extension_mapper[extension]
  paths = Data()
  setattr(paths, field, data)
  return paths


SETUP_DATA = {
  'str': case_setup_data_for_str,
  'dict': lambda data: dacite.from_dict(Data, data),
  'dataclass': lambda data: data,
}


def setup_data(data: Data | dict | str) -> Data:
  '''Returns a dataclass for dictionary, string, or dataclass inputs passed into 
  main function'''
  cases = {
    isinstance(data, dict): 'dict',
    hasattr(data, '__dataclassfields__'): 'dataclass',
    isinstance(data, str): 'str',
  }
  _case = cases[1]
  function = SETUP_DATA[_case]
  return function(data=data)


GET_ASSOCIATED_PATH = {
  '.yml': lambda data: data.replace('.yml', '.py'),
  '.yaml': lambda data: data.replace('.yaml', '.py'),
  '.py': lambda data: data.replace('.py', '.yml'),
  None: lambda data: None
}


def get_associated_path(data: str) -> str:
  '''Return the yaml path associated with a python path, or vice versa'''
  extension = get_file_extension(data=data)
  function = GET_ASSOCIATED_PATH[extension]
  return function(data=data)


def set_missingfield_path(data: Data) -> Data:
  '''Returns a dataclass. Fills in missing path or yaml path for instances where
  only one of them is set'''
  fields = {'py_path': 'yml_path', 'yml_path': 'py_path'}
  for field, associatedfield in fields.items():
    field_value = getattr(data, field)
    if field_value is not None:
      continue
    associatedfield_value = getattr(data, associatedfield)
    field_value = get_associated_path(data=associatedfield_value)
    setattr(data, field, field_value)
  return data


def main(data: Data | dict | str) -> Data | Any:
  '''Returns the and python and yml paths'''
  data = setup_data(data=data)
  data = set_missingfield_path(data=data)
  return data


def example() -> None:
  from time import time


  data = __file__
  start_time = time()
  data = main(data=data)
  end_time = time() - start_time
  print(f'runtime: {end_time * 1000} ms', data, sep='\n')


if __name__ == '__main__':
  example()

from typing import List, Dict, Any


def convert_strings_to_modules(
  inputs: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
  switcher = {
    '__builtins__': __builtins__,
  }
  for i in range(len(inputs)):
    modules = inputs[i]['modules']
    for j in range(len(modules)):
      modules[j] = switcher[modules[j]]
    inputs[i]['modules'] = modules
  return inputs


def convert_strings_to_objects(
  inputs: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
  switcher = {
    'str': str,
    'int': int,
    'float': float,
  }
  for i in range(len(inputs)):
    cast_object = inputs[i]['cast_object']
    inputs[i]['cast_object'] = switcher[cast_object]
  return inputs


if __name__ == '__main__':
  inputs = [dict(value=1, cast_object='str', unpack=False)]
  inputs = convert_strings_to_objects(inputs=inputs)
  print(inputs)

  inputs = [dict(modules=['__builtins__'], cast_object_name='str')]
  inputs = convert_strings_to_modules(inputs=inputs)
  print(inputs)


#!/usr/bin/env python

from typing import List, Dict, Any, Callable
from types import ModuleType
from pydantic import BaseModel
from dataclasses import dataclass
# import json
# import yaml
# from unittest import mock
from copy import deepcopy
# from importlib.machinery import SourceFileLoader

# TODO - Rename to format_output to format_data
from shared.format_data import app as format_output
from shared.get_module_at_path import (
  app as get_module_at_path)


@dataclass
class Patch:
  function: str = None
  return_value: Any = None


# TODO - Testing Framework: dyanically patch functions
class Patch(BaseModel):
  module: Any = None
  function: str = None
  return_value: Any = None
  side_effect: Any = None


class Data(BaseModel):
  # module: ModuleType = None
  # module: Any = None
  module: str = None
  module_path: str = None
  function: Callable = None
  data: Any = None
  unpack_data: bool = False
  patches: List[Patch] = None
  patched_function: List[Dict[str, Any]] = None
  processed_data: Any = None
  restored_functions: List[str] = None


# def bind_return_value_to_function(return_value: Any) -> Any:
#   # Bind the return value to a lambda that 
#   # can accept any arrangement of arguements
#   return lambda *args, **kwargs: return_value
#   # return lambda *x: return_value


def process_data(
  data: Any,
  function: Callable,
  data_basemodel: BaseModel = None,
  unpack_data: bool = False, 
) -> Any:
  # Unpack dictionary into BaseModel
  if data_basemodel is not None and isinstance(data, dict):
    data = data_basemodel(**data)
    return function(data)
  # Unpack dictionary 
  if unpack_data is True and isinstance(data, dict):
    return function(**data)
  return function(data)


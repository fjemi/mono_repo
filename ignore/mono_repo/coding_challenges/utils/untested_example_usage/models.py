#!/usr/bin/env python

from typing import List, Dict, Any, Callable
from types import ModuleType
from pydantic import BaseModel


class Patch(BaseModel):
  function_name: str = None
  return_value: Any = None


class Import(BaseModel):
  module_path: str = None
  module_name: str = None
  function_name: str = None


class Test(BaseModel):
  function_name: str = None
  description: str = None
  notes: str = None
  imports: List[Dict[str, str] | Import] = None
  patches: List[Dict[str, str] | Patch] = None
  pre_process_inputs: List[Dict[str, str] | Patch] = None
  inputs: List[Any] = None
  cast_inputs_as: str = None
  outputs: List[Any] = None
  cast_outputs_as: str = None


class Data(BaseModel):
  module_path: str = None
  yml_path: str = None
  description: str = None
  notes: str = None
  tests: List[Test] = None


if __name__ == '__main__':
  from shared.get_data_from_path import app as get_data_from_path
  from shared.format_data import app as format_data


  data = __file__.replace('.py', '.yml')
  data = get_data_from_path.main(data=data)
  data = Data(**data)
  data = format_data.main(data=data)
  print(data)

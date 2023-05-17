#!/usr/bin/env python3

from typing import List, Dict, Any, Callable
from pydantic import BaseModel
import json
import yaml
from unittest import mock
from importlib.machinery import SourceFileLoader
from types import ModuleType

from shared.format_data import app as format_output
from shared.patch_function import app as patch_function
from shared.get_module_and_yml_paths import app as get_module_and_yml_paths
from shared.get_data_from_path import app as get_data_from_path
from shared.get_module_at_path import app as get_module_at_path
from shared.cast_data_as import app as cast_data_as


# TODO - Testing Framework: dyanically patch functions
class Patch(BaseModel):
  function: str = None
  return_value: Any = None
  # side_effect: Any = None


class Function(BaseModel):
  name: str = None
  description: str = None
  notes: str = None
  imports: List[Dict[str, str]] | Dict[str, str] | None = None
  patches: List[Dict[str, str]] | Dict[str, str] | None = None
  cast_inputs_as: List[str] | str | None = None
  inputs: List[Any] | Any | None = None
  outputs: List[Any] | Any | None = None
  unpack: List[bool] | bool | None = None
  cast_outputs_as: List[str] | str | None = None
  assertations: List[str] | str | None = None
  results: List[str] | str | None = None


class Data(BaseModel):
  paths: Any = None
  module_path: str = None
  yml_path: str = None
  module_vars: Dict[str, Any] = None
  # functions: List[Dict[str, Any]] | List[Function] = None
  functions: List[Dict] = None



# TODO: Switch/case {input_type, output_type, output_cast_as}
# TODO: Ties into the Testing Framework
def main(
  data_set: List[Dict[Any, Any]] = None, 
  function: Callable = None,
  cast_inputs_as: BaseModel = None,
  cast_outputs_as: bool = True,
  yml_path: str = None,
  module_path: str = None,
  module_vars: Dict[str, Any] = None,
  # outputs_cast_as instead of cast_outputs_as
) -> Any:

  # Set file paths
  paths = get_module_and_yml_paths.main(
    yml_path=yml_path,
    module_path=module_path,
  )

  # Get yml data
  yml_data = get_data_from_path.main(data=paths.yml)
  data = Data(functions=yml_data['functions'])

  # Import module to test
  # module = get_module_at_path.main(data=dict(
  #   module_name='app',
  #   module_path=paths.module,
  # ))

  for function_data in data.functions:
    # Import module to test
    module = get_module_at_path.main(data=dict(
      module_name='app',
      module_path=paths.module,
    ))

    # Import any modules needed to run tests
    # print(function_data.imports)

    # Setup patches to prevent errors
    if function_data.patches is None:
      function_data.patches = []
    # Patch functions
    module = patch_function.patch_functions(
      module_path=paths.module,
      module=module, 
      patches=function_data.patches,
    )
    module_vars = vars(module)
    # print(vars(module)['input']())
    # print(module.get_cli_input())

    # Cast inputs
    # Process data
    # Format output
    # Compare output
    # Reload module

    # function_data = Function(**function_data)
    function = module_vars[function_data.name]
    
    outputs_store = []
    for inputs in function_data.inputs:
      if function_data.cast_inputs_as is None:
        output = function(**inputs)
        outputs_store.append(output)
        continue

      if function_data.cast_inputs_as is not None:
        basemodel = module_vars[function_data.cast_inputs_as]
        inputs = basemodel(**inputs)
        output = function(inputs)
        outputs_store.append(output)
        continue
    
    if function_data.cast_outputs_as is True:
      print(list(function_data.__fields__.keys()))
      for i in range(len(outputs_store)):
        outputs_store[i] = outputs_store[i].dict()

    data = dict(
      function=function_data.name,
      # description=function_data.description,
      inputs=function_data.inputs, 
      outputs=outputs_store
    )
    if function_data.cast_outputs_as is not False:
      data['cast_outputs_as'] = function_data.cast_outputs_as
    if function_data.cast_inputs_as is not None:
      data['cast_inputs_as'] = function_data.cast_inputs_as

    print(format_output.main(data=data))
    

  if data_set is None:
    return

  store = []
  for data in data_set:

    if cast_inputs_as is not None and cast_outputs_as is False:
      data = cast_inputs_as(**data)
      result = function(data)
      store.append(result)
      continue

    if cast_inputs_as is not None and cast_outputs_as is True:
      data = cast_inputs_as(**data)
      result = function(data)
      result = result.dict()
      store.append(result)
      continue

    if cast_inputs_as is None and cast_outputs_as is True:
      result = cast_inputs_as(**data)
      result = result.dict()
      store.append(result)
      continue

    if cast_inputs_as is None and cast_outputs_as is False:
      result = cast_inputs_as(**data)
      store.append(result)
      continue


# FUNCTION_DATA_SWITCHER = {
#   'Function':lambda function: list(function)
#   'dict': lambda function: list(Function(**function))
# }


def setup_function_data(functions: List[Dict] | Dict) -> List[Function]:
  if functions is None:
    return []
  # # Signle item to a list
  # if isinstance(functions, list) is False:
  #   functions = list(functions)
  # # Cast dictionaries to dataclasses
  # for i in range(len(functions)):
  #   functions[i] = Function(**functions[i])
  return functions


if __name__ == '__main__':
  
  
  yml_path = '/home/femij/mono_repo/coding_challenges/coding_challenges/yahtzee/app.yml'
  paths = get_module_and_yml_paths.main(data=yml_path)
  # print(paths)

  # Get yml data
  yml_data = get_data_from_path.main(paths.yml_path)
  functions = yml_data['functions']
  functions = setup_function_data(functions=functions)

  # Preprocess inputs

  # Cast inputs
  for i in range(len(functions)):
    function = Function(**functions[i])
    # Cast function inputs
    # for key, value in functions[i].items():
    #   print(key, value)
    print(function.cast_inputs_as)
    function.inputs = cast_data_as.main(dict(
      modules=[locals],
      values=function.inputs,
      unpack=function.unpack,
      cast_object_names=function.cast_inputs_as,
    ))
    print(function.inputs)
  print(functions)
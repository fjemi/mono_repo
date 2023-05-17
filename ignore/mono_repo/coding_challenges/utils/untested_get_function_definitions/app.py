#!/usr/bin/env python3

import ast
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable, Any
import dacite

from shared.untested_error_handler import app as error_handler


FUNCTION_DEFINITION_ATTRIBUTES_MAP = {
  'name': 'name',
  'args': 'args',
  'body': 'body',
  'decorator_list': 'decorators', 
  'returns': 'return_type',
  'type_comment': 'type_comment',
}


@dataclass
class Data:
  module_path: str = ''
  function_definitions: List[Tuple[str, Callable] | List[str]] = field(
    default_factory=lambda: [])
  output_attributes: str | List[str] | None = None


SETUP_DATA_SWITCHER = {
  'Data': lambda _locals: _locals['data'],
  'dict': lambda _locals: dacite.from_dict(Data, _locals['data']),
  'str': lambda _locals: Data(module_path=_locals['data']),
  'NoneType': lambda _locals: Data(
    module_path=_locals['module_path'],
    output_attributes=_locals['output_attributes'],
  )
}


# @error_handler.main
def setup_data(_locals: Dict[str, Any]) -> Data:
  '''Formats data passed into the main function of this module,
  to facilitate processing downstream'''
  data_type = type(_locals['data']).__name__
  function = SETUP_DATA_SWITCHER[data_type]
  return function(_locals=_locals)


# @error_handler.main
def get_abstract_syntax_tree(module_path: str) -> List[Any]:
  '''Returns the abstract syntax (ast) tree for a 
  module given the module's path'''
  with open(module_path, 'r') as file:
    source = file.read()
    return ast.parse(source).body


# @error_handler.main
def get_function_definitions(
  abstract_syntax_tree: str,
  module_path: str,
) -> List[ast.FunctionDef]:
  '''Returns a list a the user defined functions from a modules ast'''
  store = []
  for member in abstract_syntax_tree:
    if isinstance(member, ast.FunctionDef):
      store.append(member)
  return store


# @error_handler.main
def get_function_definition_returns(
  function_definition: ast.FunctionDef,
) -> str:
  '''Returns the return type (str, list, dict, ect)
   from a function definition'''
  return function_definition.returns.id


# @error_handler.main
def get_function_definition_name(
  function_definition: ast.FunctionDef,
) -> str:
  '''Returns the name from  a function definition'''
  return function_definition.name


# @error_handler.main
def get_function_definition_type_comment(
  function_definition: ast.FunctionDef,
) -> str:
  '''Returns comments from a function definition'''
  return function_definition.type_comment


# @error_handler.main
def get_function_definition_decorator_list(
  function_definition: ast.FunctionDef,
) -> str:
  '''Format and return a list of decorators from a function definition'''
  n = len(function_definition.decorator_list)
  for i in range(n):
    decorator_name = function_definition.decorator_list[i].value.id
    decorator_attribute = function_definition.decorator_list[i].attr
    function_definition.decorator_list[i] = dict(
      decorator_name=decorator_name,
      decorator_attribute=decorator_attribute,
    )
  return function_definition.decorator_list


# @error_handler.main
def get_function_definition_args(
  function_definition: ast.FunctionDef,
) -> List[Dict]:
  '''Format and return argument data (name, type, default value) 
  from a function definition.'''
  function_definition_args = function_definition.args
  args = function_definition_args.args
  defaults = function_definition_args.defaults

  store = []
  # Set argument data
  for arg in args:
    # Get the argument type hint
    argument_type = None
    if hasattr(arg.annotation, 'id'):
      argument_type = getattr(arg.annotation, 'id')
    
    # Store argument data as a dictionary
    argument_data = dict(
      argument=arg.arg,
      type=argument_type,
      default_value=None,
    )
    store.append(argument_data)

  # Set any arguments with default values
  n = len(defaults)
  for i in range(n):
    store[i]['default_value']= defaults[i].value

  return store


# @error_handler.main
def get_function_definition_body(
  function_definition: ast.FunctionDef,
) -> str:
  '''Return the body form a function definition'''
  # TODO: Format body output
  # n = len(function_definition.body)
  # for i in range(n):
  #   print(ast.dump(function_definition.body[i]))
  return function_definition.body


# @error_handler.main
def get_function_definition_attribute(
  attributes: str, 
  function_definitions: List[ast.FunctionDef],
  _locals: Dict = locals(),
) -> Dict[str, List[Any]]: 
  '''Returns a list '''
  store = {}
  for attribute in attributes:
    values = []
    # attribute = FUNCTION_DEFINITION_ATTRIBUTES_MAP[attribute]
    # Setup switcher
    function_name = f'get_function_definition_{attribute}'
    function = _locals[function_name]
    # Get function definition attributes
    for function_definition in function_definitions:
      value = function(function_definition=function_definition)
      values.append(value)
    store[attribute] = values
  return store


FORMAT_OUTPUT_SWITCHER = {
  'NoneType': lambda output_attributes: [],
  'list': lambda output_attributes: output_attributes,
  'str': lambda output_attributes: [output_attributes],
}


# @error_handler.main
def format_output(data: Data) -> Any:
  ''''''
  data_type = type(data.output_attributes).__name__
  switcher = FORMAT_OUTPUT_SWITCHER[data_type]
  data.output_attributes = switcher(output_attributes=data.output_attributes)

  if data.output_attributes == []:
    data.output_attributes = list(FUNCTION_DEFINITION_ATTRIBUTES_MAP.keys())

  if 'name' not in data.output_attributes:
    data.output_attributes = ['name'] + data.output_attributes 

  return get_function_definition_attribute(
    attributes=data.output_attributes,
    function_definitions=data.function_definitions,
  )


# @error_handler.main
def main(
  data: Dict | Data | str | None = None, 
  module_path: str | None = None,
  output_attributes: List[str] | None = None,
) -> Dict[str, List[Any]]:
  '''An orchestration function used to execute the functions within this module
  and return information about a module's functions'''
  data = setup_data(_locals=locals())
  abstract_syntax_tree = get_abstract_syntax_tree(module_path=data.module_path)
  data.function_definitions =  get_function_definitions(
    abstract_syntax_tree=abstract_syntax_tree,
    module_path=data.module_path,
  )
  return format_output(data=data)


def example() -> None:
  module_path = '/home/femij/mono_repo/coding_challenges/utils/patch_object/test_resources/app.py'
  data = Data(
    module_path=module_path, 
    output_attributes=[],
  )
  data = main(data)
  print(data)


if __name__ == '__main__':
  example = example()

#!/usr/bin/env python3

import dataclasses as dc
from typing import Any, Callable, List, Dict
from types import ModuleType
import dacite

from app import get_module_at_path
from app import error_handler


@dc.dataclass(slots=True)
class Tree:
  parent_object: object | Dict = None
  child_object_name: str = None


@dc.dataclass(slots=True)
class Patch:
  object_name: str | None = None
  return_value: Any | None = None
  value: Any | None = None
  side_effect: List | Dict | None = None


@dc.dataclass(slots=True)
class Data:
  modules: Dict[str, ModuleType] = dc.field(default_factory=lambda: {})
  module_paths: List[str] | str = dc.field(default_factory=lambda: [])
  patches: List[Patch] | Patch = dc.field(default_factory=lambda: [])


SETUP_DATA = {
  'dict': lambda data: dacite.from_dict(Data, data),
  'dataclass': lambda data: data,
  'NoneType': lambda data: Data(),
}


## @error_handler.main
def setup_data(data: Data | dict) -> Data:
  '''Returns a dataclass for different inputs into the main function'''
  cases = {
    isinstance(data, dict) is True: 'dict',
    hasattr(data, '__dataclassfields__') is True: 'dataclass',
    data is None: 'NoneType',
  }
  _case = cases[1]
  function = SETUP_DATA[_case]
  return function(data=data)


IS_LIST = {
  1: lambda value: value,
  0: lambda value: [value],
}


## @error_handler.main
def convert_single_item_to_list(data: Data) -> Data:
  '''Converts fields with single values into a list containing the single item
  to facilitate processing down stream'''
  exclude = ['modules']
  for dataclassfield in dc.fields(data):
    if dataclassfield.name in exclude:
      continue
    value = getattr(data, dataclassfield.name)
    _case = isinstance(value, list)
    function = IS_LIST[_case]
    value = function(value=value)
    setattr(data, dataclassfield.name, value)
  return data


IS_A_TEST_RESOURCE = {
  0: lambda name: name.replace('.', '_'),
  1: lambda name: name.split('.')[-1],
}


## @error_handler.main
def get_modules(data: Data) -> Dict[str, ModuleType]:
  '''Returns a dictionary values being python modules and keys being the name
  of the modules.
  
  The key for the module to test will be the file name of the module, and the 
  key for modules from the test_resources directory with be the module's file
  name with the prefix <test_resources_>'''
  # Modules passed in
  if data.modules:
    data.modules['__builtins__'] = __builtins__
    return data.modules
  
  store = {}
  for module_path in data.module_paths:
    module = get_module_at_path.main(module_path)
    # Set module name
    _case = module.name.find('test_resources') == -1
    module_name = IS_A_TEST_RESOURCE[_case](name=module.name)
    # Add module to store
    store[module_name] = module._object
  # Add builtins module
  store['__builtins__'] = __builtins__
  return store


## @error_handler.main
def case_bind_return_value(return_value: Any) -> Callable:
  '''Returns a function that produces a return value when called with any
  combination of inputs.'''
  # Use args/kwargs to allow the function to 
  # accept any arrangement of inputs
  return lambda *args, **kwargs: return_value


## @error_handler.main
def get_side_effect_value_and_increment_count(side_effect: Dict) -> Any:
  '''Returns a value of from the side effect list at index count, and increments
  count for the next value'''
  # Get the value and increment counter
  index = side_effect['count']
  value = side_effect['values'][index]
  side_effect['count'] += 1
  # Reset counter once it exceeds number of elements
  n = len(side_effect['values'])
  if side_effect['count'] > n - 1:
    side_effect['count'] = 0
  return value


# TODO: Handle multiple side effects: `function_name.side_effect`
## @error_handler.main
def case_bind_side_effect_list(side_effect: List[Any]) -> Callable:
  '''Returns a function that uses a list side effect. The list '''
  # Handle multiple side effects
  # if 'side_effect' in globals().keys():
  #   message = 'A list side effect already exists. Only one can be used per test'
  #   raise RuntimeError(message)
  
  # Add side effect and counter as global variables
  globals()['side_effect'] = {
    'values': side_effect,
    'count': 0,
  }

  return lambda *args, **kwargs: get_side_effect_value_and_increment_count(
    side_effect=globals()['side_effect'],
  )
  

## @error_handler.main
def case_bind_side_effect_dict(side_effect: Dict[Any, Any]) -> Callable:
  '''Returns a function that uses a dictionary side effect. When a key in the 
  dictionary is the passed into the function, the value associated with the key
  is returned'''
  return lambda key: side_effect[key]


## @error_handler.main
def case_bind_value(data: Any) -> Any:
  return data


GET_BIND_OBJECT = {
  'value': case_bind_value,
  'return_value': case_bind_return_value,
  'side_effect_list': case_bind_side_effect_list,
  'side_effect_dict': case_bind_side_effect_dict,
}


## @error_handler.main
def get_bind_object(
  value: Any = None,
  side_effect: Dict | List = None,
  return_value: Any = None,
) -> Callable | Any | object | None:
  '''Returns the bind function for patching based on values for the 
  `return_value` or `side_effect`'''
  if side_effect is not None:
    _type = type(side_effect).__name__
    _case = f'side_effect_{_type}'
    function = GET_BIND_OBJECT[_case]
    return function(side_effect)
  
  if return_value is not None:
    _case = 'return_value'
    function = GET_BIND_OBJECT[_case]
    return function(return_value)

  if value is not None:
    _case = 'value'
    function = GET_BIND_OBJECT[_case]
    return function(value)


def case_parent_object_is_dict(
  parent_object: Dict,
  child_object_name: str,
) -> object | Callable | None:
  if child_object_name in parent_object.keys() is True:
    return parent_object[child_object_name]


def case_parent_object_is_object(
  parent_object: object,
  child_object_name: str,
) -> object | Callable | None:
  if hasattr(parent_object, child_object_name) is True:
    return getattr(parent_object, child_object_name)


GET_ATTRIBUTE_OR_VALUE = {
  'dict': lambda parent, child_name: parent[child_name],
  'module': lambda parent, child_name: getattr(parent, child_name),
}


## @error_handler.main
def get_object_tree(
  object_name: str, 
  _globals: dict,
) -> Tree:
  # List of names parent modules or dictionaries 
  # for the object to be patched
  object_names = object_name.split('.')
  n = len(object_names) - 1
  # Store parent objects starting with globals
  parents = [globals()]
  # Populate list of parent objects 
  for i in range(n):
    child_name = object_names[i]
    last_parent = parents[-1]
    _case = type(last_parent).__name__
    function = GET_ATTRIBUTE_OR_VALUE[_case]
    parent = function(
      parent=last_parent, 
      child_name=child_name,
    )
    parents.append(parent)
  return Tree(
    parent_object=parents[-1],
    child_object_name=object_names[-1],
  )


## @error_handler.main
def set_patches(data: Data, _globals: dict) -> Dict:
  '''Patches objects; binds the object to a value or a callable return value or
  side effect.'''
  for patch in data.patches:
    object_tree = get_object_tree(
      object_name=patch.object_name,
      _globals=_globals,
    )
    bind_object = get_bind_object(
      value=patch.value,
      return_value=patch.return_value,
      side_effect=patch.side_effect,
    )
    parent_type = type(object_tree.parent_object).__name__
    if parent_type == 'dict':
      object_tree.parent_object[object_tree.child_object_name] = bind_object
    else:
      setattr(
        object_tree.parent_object, 
        object_tree.child_object_name, 
        bind_object,
      )
  return _globals


## @error_handler.main
def main(data: Data) -> Dict[str, ModuleType]:
  '''Patches objects within modules and returns the modified modules within a
  dictionary'''
  # Setup and format data
  data = setup_data(data=data)
  data = convert_single_item_to_list(data=data)
  # Load modules from path
  data.modules = get_modules(data=data)
  for key, value in data.modules.items():
    globals()[key] = value
  # Patch objects
  _globals = set_patches(data=data, _globals=globals())
  for key in data.modules:
    data.modules[key] =_globals[key]
  return data.modules


def example() -> None:
  import yaml


  data = '''
    module_paths:
    - /home/femij/mono_repo/coding_challenges/utils/patch_object/app.py
    - /home/femij/mono_repo/coding_challenges/utils/untested_test_cases/test_resources/arithmetic.py
    patches:
    - object_name: test_resources_arithmetic.use_add
      value: use_add_patched
    - object_name: __builtins__.input
      value: use_add_input
    - object_name: test_resources_arithmetic.add
      return_value: add_patched
    - object_name: test_resources_arithmetic.subtract
      side_effect: 
      - subtract_patched_0
      - subtract_patched_1
      - subtract_patched_2
    - object_name: test_resources_arithmetic.foo
      side_effect: {0: foo_patched_0, 1: foo_patched_1, 2: foo_patched_2}
    - object_name: test_resources_arithmetic.foo_bar
      return_value: [foo_patched_0, foo_patched_1, foo_patched_2]
  '''
  data = yaml.safe_load(data)
  data = main(data=data)
  
  example = dict(
    value=[
      data['test_resources_arithmetic'].use_add,
      data['__builtins__'].input,
    ],
    return_value=[
      data['test_resources_arithmetic'].add(),
      data['test_resources_arithmetic'].foo_bar(),
    ],
    side_effect_list=[
      data['test_resources_arithmetic'].subtract(),
      data['test_resources_arithmetic'].subtract(),
      data['test_resources_arithmetic'].subtract(),
      data['test_resources_arithmetic'].subtract(),
    ],
    side_effect_dict=[
      data['test_resources_arithmetic'].foo(0),
      data['test_resources_arithmetic'].foo(1),
      data['test_resources_arithmetic'].foo(2),
    ],
  )
  
  example = yaml.dump(dict(example=example), indent=2)
  print(example, sep='\n')


if __name__ == '__main__':
  example()

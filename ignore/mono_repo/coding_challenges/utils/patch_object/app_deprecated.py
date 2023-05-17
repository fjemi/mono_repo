#!/usr/bin/env python3

from dataclasses import dataclass, field, fields
from typing import Any, Callable, List, Dict
from types import ModuleType
import dacite

from shared.get_module_at_path import app as get_module_at_path


@dataclass(slots=True)
class Object:
  name: str = None
  _type: str = None
  value: ModuleType | Callable | Dict | Any = None
  

@dataclass(slots=True)
class Patch:
  object_name: str | None = None
  return_value: Any | None = None
  value: Any | None = None
  side_effect: List | Dict | None = None


@dataclass(slots=True)
class ObjectHierarchy:
  parent: Object = None
  child: Object = None


@dataclass(slots=True)
class Data:
  # modules: List[Object] | Object | None = field(default_factory=lambda: [])
  patches: List[Patch] | Patch | None = field(default_factory=lambda: [])
  object_hierarchies: List[ObjectHierarchy] | ObjectHierarchy | None = field(
    default_factory=lambda: [])
  # object_hierarchy: List[Object] | Object = field(default_factory=lambda: [])
  patched: List[bool] | bool | None = field(default_factory=lambda: [])
  reverted: List[bool] | bool | None = field(default_factory=lambda: [])


SETUP_DATA = {
  'dict': lambda data: dacite.from_dict(Data, data),
  'dataclass': lambda data: data,
  'NoneType': lambda data: Data(),
}


def setup_data(data: Data | dict) -> Data:
  '''Returns a dataclass for different inputs into the main function'''
  cases = {
    isinstance(data, dict) is True: 'dict',
    hasattr(data, '__dataclass_fields__') is True: 'dataclass',
    data is None: 'NoneType',
  }
  _case = cases[1]
  function = SETUP_DATA[_case]
  return function(data=data)


SINGLE_FIELD_ITEMS_TO_LIST = {
  'list_True': lambda value: value,
  'list_False': lambda value: [value],
}

def single_field_items_to_list(data: Data) -> Data:
  '''Converts fields with single values into a list containing the single item
  to facilitate processing down stream'''
  for dataclass_field in fields(data):
    value = getattr(data, dataclass_field.name)
    _case = f'list_{isinstance(value, list)}'
    function = SINGLE_FIELD_ITEMS_TO_LIST[_case]
    value = function(value=value)
    setattr(data, dataclass_field.name, value)
  return data


def case_bind_return_value(return_value: Any) -> Callable:
  '''Returns a function that produces a return value when called with any
  combination of inputs.'''
  # Use args/kwargs to allow the function to 
  # accept any arrangement of inputs
  return lambda *args, **kwargs: return_value


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
  

def case_bind_side_effect_dict(side_effect: Dict[Any, Any]) -> Callable:
  '''Returns a function that uses a dictionary side effect. When a key in the 
  dictionary is the passed into the function, the value associated with the key
  is returned'''
  return lambda key: side_effect[key]


def case_bind_value(data: Any) -> Any:
  return data


GET_BIND_OBJECT = {
  'value': case_bind_value,
  'return_value': case_bind_return_value,
  'side_effect_list': case_bind_side_effect_list,
  'side_effect_dict': case_bind_side_effect_dict,
}


def get_bind_object(
  value: Any = None,
  side_effect: Dict | List = None,
  return_value: Any = None,
) -> Callable | Any:
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


def case_parent_object_is_module(
  parent: ModuleType, 
  object_name: str,
) -> Any | None:
  '''Returns an object form a parent object for cases where the parent object is
  a module, or `None` if the object doesn't exist within the parent.'''
  if hasattr(parent, object_name) is True:
    return getattr(parent, object_name)


def case_parent_object_is_dict(
  parent: Dict, 
  object_name: str,
) -> Any | None:
  '''Returns an object form a parent object for cases where the parent object is
  a dictionary, or `None` if the object doesn't exist within the parent.'''
  if object_name in parent.keys():
    return parent[object_name]


def case_parent_object_is_none(
  parent: Dict = None, 
  object_name: str = None,
) -> None:
  '''Returns `None` for cases where the parent object is `None` or the object to
  patch does not exist in the parent object.'''
  # message = f'`{object_name}` does not exist!'
  # raise RuntimeError(message)
  return None


GET_OBJECT_HIERARCHY = {
  'function': lambda parent, object_name: getattr(parent, object_name),
  'module': case_parent_object_is_module,
  'dict': case_parent_object_is_dict,
  'NoneType': case_parent_object_is_none,
}


def get_object_hierarchy(
  object_name: str, 
  _locals: Dict = locals(),
) -> ObjectHierarchy:
  '''Returns the hierarchy for an object; parent-child relationship'''
  # Object hierarchy as a list of strings
  object_names = object_name.split('.')

  # Add locals for processing downstream
  parent_object = Object(
    _type='dict', 
    value=_locals, 
    name='locals',
  )
  hierarchy = [parent_object]
  
  # Get the rest of the object's hierarchy
  n = len(object_names)
  for i in range(0, n):
    parent_object = hierarchy[-1]
    function = GET_OBJECT_HIERARCHY[parent_object._type]
    child_name = object_names[i]
    child_value = function(
      parent=parent_object.value, 
      object_name=child_name,
    )
    child_type = type(child_value).__name__
    child_object = Object(
      value=child_value,
      _type=child_type,
      name=child_name,
    )
    hierarchy.append(child_object)
  
  return ObjectHierarchy(
    parent=hierarchy[-2],
    child=hierarchy[-1],
  )


def case_patch_when_parent_object_is_module(
  parent_object: Dict,
  object_name: str,
  bind_object: Callable | Any,
) -> bool:  
  '''Returns True after patching an object for cases where the parent object
  is a module'''
  if hasattr(parent_object, object_name) is True:
    setattr(parent_object, object_name, bind_object)
    return True
  return False


def case_patch_when_parent_object_is_dict(
  parent_object: Dict,
  object_name: str,
  bind_object: Callable | Any,
) -> bool:
  '''Returns True after patching an object for cases where the parent object
  is a dictionary'''
  if object_name in parent_object.keys():
    parent_object[object_name] = bind_object
    return True
  return False


PATCH_OBJECT = {
  'module': case_patch_when_parent_object_is_module, 
  'dict': case_patch_when_parent_object_is_dict,
  'NoneType': lambda *args, **kwargs: False,
}


def patch_object(
  object_hierarchy: ObjectHierarchy, 
  bind_object: Callable | Any,
) -> bool:
  '''Patches an object within a module or dictionary and returns True'''
  function = PATCH_OBJECT[object_hierarchy.parent._type]
  return function(
    parent_object=object_hierarchy.parent.value, 
    object_name=object_hierarchy.child.name, 
    bind_object=bind_object,
  )


REVERT_PATCHES = {
  True: lambda object_hierarchy, bind_object: patch_object(
    object_hierarchy=object_hierarchy,
    bind_object=bind_object,
  ),
  False: lambda object_hierarchy, bind_object: None,
}

# TODO: Find out if this is needed if each test is run within its own thread
def revert_patches(data: Data) -> Data:
  '''Reverts patched objects to their original functionality'''
  n = len(data.patched)
  store = []
  for i in range(n):
    function = REVERT_PATCHES[data.patched[i]]
    reverted = function(
      object_hierarchy=data.object_hierarch[i],
      bind_object=data.object_hierarchy[i][-1].value,
    )
    store.append(reverted)
  data.reverted = store
  return data


def main(
  data: Data | dict, 
  _locals: Dict = locals(), 
  # revert: bool = False,
) -> Data:
  '''An orchestration function that patches objects or revert patches, using
  the other functions defined within this module'''
  # Setup data
  data = setup_data(data=data)

  # # Revert patches
  # if revert is True:
  #   data = revert_patches(data=data)
  #   return data

  # Patch objects
  data = single_field_items_to_list(data=data)
  for patch in data.patches:
    bind_object = get_bind_object(
      value=patch.value,
      side_effect=patch.side_effect,
      return_value=patch.return_value,
    )
    # Get object hierarchy
    object_hierarchy = get_object_hierarchy(
      object_name=patch.object_name,
      _locals=_locals,
    )
    data.object_hierarchies.append(object_hierarchy)
    # Patch the object
    patched = patch_object(
      object_hierarchy=object_hierarchy,
      bind_object=bind_object,
    )
    data.patched.append(patched)
  return data


def example() -> None:
  from test_resources import app as test_resources
  import os
  import builtins
  import json

  data = {}

  patches = [
    dict(
      object_name='test_resources.dictionary_module.add', 
      side_effect={'add': 'add_patched'},
    ),
    dict(
      object_name='test_resources.dictionary_module.subtract', 
      side_effect={'subtract': 'subtract_patched'},
    ),
    dict(
      object_name='test_resources.add', 
      return_value='test_resources.add_patched',
    ),
    dict(
      object_name='builtins.int', 
      return_value='builtins.int_patched',
    ),
    dict(
      object_name='builtins.input', 
      return_value='builtins.input_patched',
    ),
    dict(
      object_name='os.path.basename', 
      return_value='os.path.basename_patched',
    ),
    dict(
      object_name='test_resources.subtract', 
      side_effect=['0', '1', '2'],
    ),
    dict(
      object_name='test_resources.variable_12', 
      value='test_resources.variable_1_patched',
    ),
    dict(
      object_name='test_resources.variable_233', 
      side_effect={0: 0},
    ),
  ]

  # Patch objects
  data['patch_data'] = dict(patches=patches)
  data['patch_data']  = main(data=data['patch_data'] , _locals=locals())
  data['patched'] = [
    test_resources.dictionary_module['add']('add'),
    test_resources.dictionary_module['subtract']('subtract'),
    os.path.basename('path'),
    builtins.int(1),
    test_resources.subtract(1, 1),
    test_resources.subtract(1, 1),
    test_resources.subtract(1, 1),
    test_resources.subtract(1, 1),
    test_resources.variable_1,
    test_resources.variable_2,
    builtins.input(),
    input(),
  ]

  # # Revert patches
  # data['reverted_data'] = main(data=data['patched'], revert=True)
  # data['reverted'] = [
  #   test_resources.dictionary_module['add'](1, 1),
  #   test_resources.dictionary_module['subtract'](1, 1),
  #   os.path.basename('path'),
  #   builtins.int('1'),
  #   test_resources.subtract(1, 1),
  #   test_resources.subtract(1, 1),
  #   test_resources.subtract(1, 1),
  #   test_resources.subtract(1, 1),
  #   test_resources.variable_1,
  #   test_resources.variable_2,
  # ]
  
  for key, value in data.items():
    print(key, value, sep='\n\n')


if __name__ == '__main__':
  example()



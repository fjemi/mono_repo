#! /usr/bin/env python3

from dataclasses import dataclass, fields, asdict, field
from typing import List, Any, Dict, Callable
from inspect import cleandoc
from types import ModuleType
import dacite
from fnmatch import fnmatch

from app import get_module_at_path


@dataclass 
class Constructor:
  '''
  description: Stores information about a constructor, an object to cast 
    another value to
  attributes:
  - name: The name of the constructor
  - _object: The constructor object imported from a module
  '''
  name: str | None = None
  _object: Any | None = None


@dataclass
class Module:
  '''
  description: Store information about a module to test
  attributes:
  - path: The path to a module
  - name: The name of a module
  - _object: The module object imported from the file path
  '''
  path: str | None = None
  name: str | None = None
  _object: ModuleType | None = None


@dataclass
class Data:
  '''
  description: Dataclass for storing information used within this module
  fields:
  - values: A list of values to cast to constructors
  - values_n: The length of the values field
  - constructors: A list of constructors that values are cast to
  - constructors_n: The length of the constructors field
  - modules: Store the module to test and the standard library
  - casted_values: A list of values casted to constructors objects
  '''
  values: List[Any] | Any | None = None
  values_n: int | None = None
  constructors: List[Constructor] | Constructor | List[str] | str | None = None
  constructors_n: int | None = None
  modules: List[Module] | Module | None = None
  casted_values: List[Any] | None = None
  value_and_cast_type_cases: List[str] | None = None
  cast_function_names: List[str] | None = None


def case_setup_data_from_dict(data: Dict) -> Data:
  '''Casts a dictionary to a dataclass and returns the resulting object'''
  return dacite.from_dict(Data, data)


def case_setup_data_from_data(data: Data) -> Data:
  '''A pass through function'''
  return data


# def case_setup_data_from_str(data: str) -> Data:
#   '''A pass through function'''
#   return Data()


def setup_data(data: Data | dict, _locals: Dict = locals()) -> Data:
  '''Converts dictionaries inputs to dataclasses for further processing 
  downstream'''
  _type = type(data).__name__
  switcher = {
    '__dataclass_fields__' in dir(data): 'data',
    _type == 'Data': 'data',
    _type == 'dict': 'dict',
    # _type == 'str': 'str',
    'keys' in dir(data): 'dict',
  }
  _case = switcher[1]
  function_name = f'case_setup_data_from_{_case}'
  function = _locals[function_name]
  return function(data)


def case_value_is_list_is_true(value: List[Any]) -> List[Any]:
  return value


def case_value_is_list_is_false(value: Any) -> List[Any]:
  return [value]


def convert_single_item_to_list(data: Data, _locals: Dict = locals()) -> Data:
  '''
  description: Converts fields with values being single items into a list
    of that single item to facilitate processing downstream. Excludes specified
    fields from the conversion.
  '''
  include = [ 
    'values', 
    'constructors',
  ]
  for field in include:
    # Get the field value and type
    value = getattr(data, field)
    _type = type(value).__name__
    function_name = f'case_value_is_list_is_{_type == "list"}'
    function_name = function_name.lower()
    function = _locals[function_name]
    value = function(value)
    setattr(data, field, value)
  return data


def get_field_lengths(data: Data) -> Data:
  '''
  description: Returns the number of items within the `constructors` and
    `values` fields
  '''
  fields = ['values', 'constructors']
  
  for field in fields:
    value = getattr(data, field)
    _type = type(value).__name__
    # Switch to handle fields with null values
    # Sets the length of the field to zero
    switcher = {
      _type == 'None': lambda: 0,
      _type != 'None': lambda: len(value)
    }
    field_name = f'{field}_n'
    setattr(data, field_name, switcher[1]())
  return data


def case_zero_to_one_or_many_relationship(
  constructors: List, 
  values_n: int,
) -> List[Constructor]:
  '''
  description: Returns a list of `Constructor` empty objects, with the number of 
    objects in the list equaling the number of items in the list for the 
    `values` field, when there is a zero to one or many relationship between 
    the number of constructors and values in the `Data` class. 
  '''
  return [Constructor() for i in range(values_n)]


def case_one_to_one_relationship(
  constructors: List[Constructor], 
  values_n: int,
) -> List[Constructor]:
  '''
  description: Returns the list of `Constructor` objects passed in when there is
    a one to one relationship between the number of items in the `constructors`
    and `values` fields.
  '''
  return constructors


def case_one_to_many_relationship(
  constructors: List[Constructor], 
  values_n: int,
) -> List[Constructor]:
  '''
  description: Returns an expanded list of the one `Constructor` object in the 
    list passed in when there is a one to many relationship between the number of 
    items in the `constructors` and `values` fields. The length of the new list
    equals that of the `values` field.
  '''
  return [constructors[0] for i in range(values_n)]


def case_many_to_many_relationship(
  constructors: List[Constructor], 
  values_n: int,
) -> None:
  '''
  description: Raises an exception when there is a many to many relationship
    between constructors and values or more constructors than values. These 
    types of relationships prevent the constructors from being expanded out to
    be the same length as the values field, which is needed for processing 
    downstream.
  '''
  message = '''There can only be a one to one or one to many relationship 
    between castors and values''' 
  # Format the message. Remove line breaks and extra spaces
  message = cleandoc(message.replace('\n', ''))
  raise RuntimeError(message)


def match_constructors_to_values_relationship(
  data: Data,
  _locals: Dict = locals(),
) -> Data:
  '''
  description: 
    Returns a list of `Constructors`, if possible. The length of the 
    list should match the length of the `values` field of the dataclass passed
    in. Uses a switch/case statement to achieve this.
  '''
  # cases and name of functions to use for them
  cases = {
    data.values_n == data.constructors_n: 'case_one_to_one_relationship',
    data.values_n > data.constructors_n and data.constructors_n == 1:
      'case_one_to_many_relationship',
    data.values_n > data.constructors_n and data.constructors_n > 1:
      'case_many_to_many_relationship',
    data.values_n < data.constructors_n: 'case_many_to_many_relationship',
    data.values_n > data.constructors_n and data.constructors_n == 0:
      'case_zero_to_one_or_many_relationship',
  }
  function_name = cases[1]
  function = _locals[function_name]
  data.constructors = function(
    constructors=data.constructors, 
    values_n=data.values_n,
  )
  return data


def set_modules_and_add_standard_library(module: Module) -> List[Module]:
  '''Returns a list containing a module import from a file path, and the 
  standard library. `Constructor` objects will be imported from the module 
  object or the standard library downstream.'''

  # Get module to test
  module = get_module_at_path.main(data=module.path)
  # Get standard library
  builtins = Module(
    name='__builtins__',
    _object=__builtins__
  )
  return [module, builtins]


def case_module_is_a_dict(
  module: Module, 
  constructor: Constructor,
) -> Constructor:
  '''Sets the the constructor object for the case where the module is a 
  dictionary and contains the'''
  constructor.name = str(constructor.name)
  # Ignore cases where the constructor name is not a key in the dictionary
  if constructor.name not in module._object.keys():
    return constructor
  constructor._object = module._object[constructor.name]
  return constructor


def case_module_is_a_module(
  module: Module, 
  constructor: Constructor,
) -> Constructor:
  '''Sets the the constructor object for the case where the module is a 
  dictionary and contains the'''
  constructor.name = str(constructor.name)
  if hasattr(module._object, constructor.name) is False:
    return constructor
  constructor._object = getattr(module._object, constructor.name)
  return constructor


def get_constructor_objects(
  modules: List[ModuleType], 
  constructors: List[Constructor],
  values_n: int,
  _locals: Dict = locals(),
) -> List[Constructor]:
  '''Imports constructor objects from a module within a list of modules and 
  returns the list of constructors.'''
  for i in range(values_n):
    # Ignore constructors with null names
    constructors[i].name = str(constructors[i].name)
    if constructors[i].name in ['None', None, 'NoneType']:
      continue

    for module in modules:
      # Get the name of the function to use to retrieve the constructor object 
      # from the module, based on the type of module: `module` or `dict`.
      module_type = type(module._object).__name__
      function_name = f'case_module_is_a_{module_type}'
      function = _locals[function_name]
      # Set the constructor object
      constructors[i] = function(
        module=module, 
        constructor=constructors[i],
      )
      # Exit nested loop if constructor object can be set
      if constructors[i]._object is not None:
        break
  return constructors


def case_value_is_none(constructor: Constructor, value: None) -> None:
  '''Returns `None` for cases where the value is `None`'''
  return None


def case_value_to_value(
  constructor: Constructor, 
  value: Any,
) -> Any:
  '''Returns the value passed in for cases where the value or constructor object
   to cast to is `None`, or the value and constructor object are of the same 
   type.'''
  return value


def case_cast_no_unpacking(constructor: Constructor, value: Any) -> Any:
  '''
  description: Returns a value casted as a constructor object for cases that 
    do not require unpacking the value (the value is not a dict, list, or tuple)
  '''
  return constructor._object(value)


def case_pydantic_initialised_in_dict_keys_is_true(data: Dict) -> Dict:
  '''Returns a dictionary with the key `__pydantic_initialized__` removed.'''
  del data['__pydantic_initialised__']
  return data


def case_pydantic_initialised_in_dict_keys_is_false(data: Dict) -> Dict:
  '''Returns the dictionary passed in. A pass through function.'''
  return data


def case_basemodel_or_dataclass_to_dict(
  constructor: Constructor, 
  value: Any,
  _locals: Dict = locals(),
) -> Any:
  '''Returns a value as a dictionary for cases where the value is a basemodel 
  or dataclass.'''
  value = value.__dict__
  _case = '__pydantic_initialised__' in value.keys()
  function_name = f'case_pydantic_initialised_in_dict_keys_is_{_case}'.lower()
  function = _locals[function_name]
  return function(data=value)


def case_dict_to_dataclass_or_basemodel(
  constructor: Constructor, 
  value: Any,
) -> Any:
  '''Returns the results of casting a dictionary value to a constructor object
  that is basemodel or dataclass'''
  # Unpack the value into the constructor object
  return constructor._object(**value)


def case_list_or_tuple_to_dataclass(
  constructor: Constructor, 
  value: Any,
) -> Any:
  '''Returns a dataclass for cases where the constructor is a dataclass and the 
  value is a list or tuple. Note: Unpacking a list/tuple into a BaseModel 
  doesn't work'''
  # Unpack the value into the constructor object
  return constructor._object(*value)


def case_list_or_tuple_to_dict(
  constructor: Constructor, 
  value: Any,
) -> Any:
  '''Returns a dictionary for cases where the value is list or tuple and the 
  constructor object is dictionary'''
  store = {}
  for a, b in value:
    store[a] = b
  return store

def case_basemodel_or_dataclass_to_other(
  constructor: Constructor, 
  value: Any,
) -> Any:
  ''''''
  return constructor._object(value)


# Switcher that selects a casting function for different
# cases of value and constructor types
FUNCTION_NAME_SWITCHER = {
  'none_to_*': 'case_value_is_none',
  '*_to_none': 'case_value_to_value',
  'other_to_other': 'case_cast_no_unpacking',
  'list|tuple_to_list|tuple': 'case_value_to_value',
  'dict_to_dict': 'case_value_to_value',
  'dataclass_to_dict': 'case_basemodel_or_dataclass_to_dict',
  'dataclass_to_other': 'case_basemodel_or_dataclass_to_other',
  'basemodel_to_dict': 'case_basemodel_or_dataclass_to_dict',
  'basemodel_to_other': 'case_basemodel_or_dataclass_to_other',
  'dict_to_dataclass': 'case_dict_to_dataclass_or_basemodel',
  'dict_to_basemodel': 'case_dict_to_dataclass_or_basemodel',
  'list|tuple_to_dataclass':'case_list_or_tuple_to_dataclass',
  'list|tuple_to_dict':'case_list_or_tuple_to_dict',
}


def get_value_and_cast_type_cases(
  values: List[Any], 
  constructors: List[Constructor], 
  values_n: int
) -> List[str]:
  '''
  description: Returns a list of strings containing the types for values and 
    constructor objects to cast them to. The strings represent the cases later
    used for determining how to cast values to constructor objects
  '''
  store = []
  for i in range(values_n):
    value = values[i]
    constructor = constructors[i]

    # Determine the constructor type based on these conditions
    constructor_conditions = {
      constructor.name in ['None', 'NoneType', None]: 'none',
      constructor.name == 'dict': 'dict',
      constructor.name in ['list', 'tuple']: 'list|tuple',
      hasattr(constructor._object, '__dataclass_fields__') is True: 'dataclass',
      hasattr(constructor._object, '__fields__') is True: 'basemodel',
      sum([
        hasattr(constructor._object, '__fields__') is False,
        hasattr(constructor._object, '__dataclass_fields__') is False,
        constructor.name not in [
          'dict', 
          'list', 
          'tuple', 
          'None', 
          'NoneType', 
          None,
        ],
      ]) / 3: 'other',
      hasattr(constructor._object, '__fields__') is True: 'basemodel',
    }
    
    # Determine the value type based on these conditions
    value_type = type(value).__name__
    value_type = value.__class__.__name__
    value_conditions = {
      value_type in ['list', 'tuple']: 'list|tuple',
      value in ['None', None, 'NoneType']: 'none',
      hasattr(value, 'keys') is True: 'dict',
      hasattr(value, '__dataclass_fields__') is True: 'dataclass',
      hasattr(value, '__fields__') is True: 'basemodel',
      sum([
        hasattr(value, 'keys') is False,
        hasattr(value, '__fields__') is False,
        hasattr(value, '__dataclass_fields__') is False,
        value_type not in ['dict', 'list', 'tuple'],
        value not in ['None', None, 'NoneType'],
      ]) / 5: 'other',
    }
    # Form the case from the value/constructor conditions
    _case = f'{value_conditions[1]}_to_{constructor_conditions[1]}'
    store.append(_case)
  return store


def get_cast_function_names(
  value_and_cast_type_cases: List[str], 
  values_n: int,
) -> List[str]:
  '''Returns a list of functions used to facilitate casting values to 
  constructor objects. Matches `value_and_cast_type_cases` to the keys of the 
  `FUNCTION_NAME_SWITCHER` dictionary to determine which function is needed.'''
  store = []
  cases = list(FUNCTION_NAME_SWITCHER.keys())
  functions = list(FUNCTION_NAME_SWITCHER.values())
  # Iterate over the keys (cases) of the 
  # `FUNCTION_NAME_SWITCHER` dictionary
  for _case in value_and_cast_type_cases:
    function = None
    for i in range(len(cases)):
      # Determine if the case matches the key at a certain index
      if fnmatch(_case, cases[i]) is False:
        continue
      # Store the function at matching index
      function = functions[i]
      break  
    store.append(function)
  return store


def get_casted_values(
  constructors: List[Constructor], 
  cast_function_names: List[str],
  values: List[Any], 
  values_n: int,
  _locals: Dict = locals(),
) -> List[Any]:
  '''Returns a list of values casted to constructor objects'''
  store = []
  for i in range(values_n):
    cast_function_name = cast_function_names[i]
    cast_function = _locals[cast_function_name]
    casted_value = cast_function(
      constructor=constructors[i],
      value=values[i],
    )
    store.append(casted_value)
  return store


def setup_constructor_data(
  constructors: List[Constructor | str],
) -> List[Constructor]:
  n = len(constructors)
  for i in range(n):
    if not isinstance(constructors[i], str):
      continue
    name = constructors[i]
    constructors[i] = Constructor(name=name)
  return constructors



def main(data: Data | dict, _locals: Dict = locals()) -> List[Any]:
  '''Casts values to specified objects and returns the results. Acts
  as an orchestrator function, executing the other functions within this 
  module in order.'''
  data = setup_data(data, _locals=_locals)
  data = convert_single_item_to_list(data=data, _locals=_locals)
  data = get_field_lengths(data=data)
  data = match_constructors_to_values_relationship(data=data, _locals=_locals)
  if data.modules is None:
    data.modules = set_modules_and_add_standard_library(module=data.modules)
  else:
    module_dataclass = Module(name='builtins', _object=__builtins__)
    data.modules.append(module_dataclass)
  data.constructors = setup_constructor_data(constructors=data.constructors)
  data.constructors = get_constructor_objects(
    modules=data.modules,
    constructors=data.constructors,
    values_n=data.values_n,
  )
  data.value_and_cast_type_cases = get_value_and_cast_type_cases(
    values=data.values, 
    constructors=data.constructors, 
    values_n=data.values_n,
  )
  data.cast_function_names = get_cast_function_names(
    value_and_cast_type_cases=data.value_and_cast_type_cases,
    values_n=data.values_n,
  )
  data.casted_values = get_casted_values(
    values=data.values,
    cast_function_names=data.cast_function_names,
    constructors=data.constructors,
    values_n=data.values_n,
    _locals=_locals,
  )
  return data.casted_values


def example() -> None:
  from pydantic import BaseModel
  from time import time


  @dataclass
  class DataClass:
    test: str = ''
  
  class Basemodel(BaseModel):
    test: str = ''


  data = dict(
    values=[
      1, 
      dict(a=1, b=2), 
      1, 
      # ((1,1), (0, 1)),
      (1,1),
      None,
      None,
      Data(),
      Basemodel(),
    ],
    constructors=[
      dict(name='str'), 
      dict(name='Standard_Dataclass'),
      dict(name='NoneType'),
      # dict(name='dict'),
      dict(name='list'),
      dict(name='NoneType'),
      dict(name='NoneType'),
      dict(name='dict'),
      dict(name='dict'),
    ],
    modules=dict(
      path='/home/femij/mono_repo/coding_challenges/utils/cast_data_as/test_resources/app.py',
    ),
  )

  start = time()
  data = main(data=data)
  end = time() - start
  print(f'{end * 1000} ms', data, sep='\n')


if __name__ == '__main__':
  example()

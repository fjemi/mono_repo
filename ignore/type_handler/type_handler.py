from dataclasses import is_dataclass, dataclass
from typing import Union, Any
from functions.exception_handler.exception_handler import exception_handler


@dataclass
class Data:
  data: Union[dict, Any] = None
  data_class: Any = None
  raise_nonetype_exception: bool = False
  instaniate_data_class: bool = False


@exception_handler
def type_handler(data: Any) -> Any:
  '''
  Summary
    Used switch/case to handle data types: 
      - none type returns none
      - dict type is unpacked into a dataclass
      - dataclass returns the dataclass
  Returns
  '''
  data = Data(data)
  print(data)

  # Case
  def case_none(data):
    if data.raise_nonetype_exception is True:
      raise AttributeError
    if data.instaniate_data_class is True:
      return data.data_class()
    return None
  def case_any(data):
    return data.data_class(data.data)
  def case_dict(data):
    return data.data_class(**data.data)
  def case_dataclass(data):
    return data.data

  # Switch
  switcher = {
    'nonetype': case_none,
    'any': case_any,
    'dict': case_dict,
    'dataclass': case_dataclass, }

  data_type = type(data.data).__name__.lower()
  if data.data_class is not None:
    data_type = 'dataclass'
  # Use any for data types other than none, dict, or dataclass
  elif data_type not in list(switcher.keys()):
    data_type = 'any'

  # Convert data to type
  handled_data = switcher[data_type](data=data)
  return handled_data

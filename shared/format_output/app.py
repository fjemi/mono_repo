#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List


@dataclass
class DataClass:
  '''Type hint for generic dataclass'''
  pass


def case_data_is_dict(data: dict) -> dict:
  remove_fields = data['remove_fields']
  for key in remove_fields:
    del data[key]
  return data


def case_data_is_dataclass(data: DataClass) -> DataClass:
  for field_name in data.remove_fields:
    setattr(data, field_name, None)
  return data
  
  
def case_data_is_none(data: None) -> None:
  return None


def remove_fields(
  data: dict | DataClass, 
  _locals: dict = locals(),
) -> dict | DataClass:
  conditions = {
    hasattr(data, '__dataclass_fields__') is True: 'dataclass',
    isinstance(data, dict) is True: 'dict',
    data is None: 'none',
  }
  _case = conditions[1]
  function_name = f'case_data_is_{_case}'
  function = _locals[function_name]
  return function(data=data)


def main(data: dict | DataClass) -> dict | DataClass:
  return remove_fields(data=data)


def example() -> None:
  data = '''
    a: a 
    b: b
    remove_fields: [a, b]
  '''
  data = main(data=data)
  print(data)
  
  
if __name__ == '__main__':
  example()
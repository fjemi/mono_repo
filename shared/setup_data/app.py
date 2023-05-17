#!/usr/bin/env python3

from os.path import expandvars
from dataclasses import dataclass
import dacite
import yaml


@dataclass
class DataClass:
  '''Type hint for generic dataclass'''
  # pylint: disable=unnecessary-pass
  pass


def case_data_is_dict(
  data: dict,
  data_class: DataClass
) -> DataClass:
  return dacite.from_dict(data_class, data)


def case_data_is_str(
  data: str,
  data_class: DataClass,
) -> DataClass:
  # Evaluate environment variables in string
  data = expandvars(data)
  data = yaml.safe_load(data)
  return case_data_is_dict(data=data, data_class=data_class)


def case_data_is_dataclass(
  data: DataClass,
  data_class: DataClass | None = None,
) -> DataClass:
  _ = data_class
  return data


def case_data_is_nonetype(
  data: None,
  data_class: DataClass,
) -> DataClass:
  _ = data
  return data_class()


def get_data_class(
  data: DataClass | dict | str,
  data_class: DataClass | None = None,
  _locals: dict = locals(),
) -> DataClass:
  conditions = {
    hasattr(data, '__dataclass_fields__') is True: 'dataclass',
    isinstance(data, dict): 'dict',
    isinstance(data, str): 'str',
    data is None: 'nonetype',
  }
  _case = conditions[1]
  function_name = f'case_data_is_{_case}'
  function = _locals[function_name]
  return function(data=data, data_class=data_class)


def main(data: dict | str, data_class: DataClass) -> DataClass:
  return get_data_class(data=data, data_class=data_class)


def example() -> None:
  @dataclass
  class Data:
    a: int = 0


  data = '''
    a: 1
  '''
  data = main(data=data, data_class=Data)
  print(data)


if __name__ == '__main__':
  example()

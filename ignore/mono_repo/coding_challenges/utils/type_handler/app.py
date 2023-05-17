#!usr/bin/env python3

from dataclasses import dataclass
import dacite
import yaml


@dataclass
class DataClass:
  '''Type hint representing a generic data class instance'''
  pass


def convert_dict_to_data(data: dict, data_class: DataClass) -> DataClass:
  '''Convert a dictionary to a dataclass'''
  return dacite.from_dict(data_class, data)


def convert_yaml_string_to_data(data: str, data_class: DataClass) -> DataClass:
  '''Convert a yaml string to a dataclass'''
  data = yaml.safe_load(data)
  return convert_dict_to_data(data=data, data_class=data_class)


def get_data_type(data: DataClass | dict | str) -> str:
  if hasattr(data, '__dataclass_fields__') is True:
    return 'DataClass'
  return type(data).__name__


SETUP_DATA_SWITCHER = {
  'DataClass': lambda data, data_class: data,
  'dict': lambda data, data_class: convert_dict_to_data(
    data=data,
    data_class=data_class,
  ),
  'str': lambda data, data_class: convert_yaml_string_to_data(
    data=data, 
    data_class=data_class,
  ),
  'NoneType': lambda data, data_class: data_class(),
}


def main(data: dict | str, data_class: DataClass) -> DataClass:
  '''Sets up arguments into the function to facilitate processing down stream'''
  data_type = get_data_type(data=data)
  switcher = SETUP_DATA_SWITCHER[data_type]
  return switcher(data=data, data_class=data_class)


def example() -> None:
  @dataclass
  class Data:
    a: int = 0


  data = Data()
  data = main(data=data, data_class=Data)
  print(data)

  data = '''a: 1'''
  data = main(data=data, data_class=Data)
  print(data)

  data = {'a': 1}
  data = main(data=data, data_class=Data)
  print(data)

  data = None
  data = main(data=data, data_class=Data)
  print(data)


if __name__ == '__main__':
  example()
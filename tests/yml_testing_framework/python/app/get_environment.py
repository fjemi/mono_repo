import dotenv
from os import path
import os
import yaml
import dataclasses as dc
from typing import Dict, Any, List
import inspect

# from app import error_handler


@dc.dataclass
class Env:
  pass


@dc.dataclass
class Data:
  file_path: str = None
  yml_path: str = None
  environment: Dict[Any, Any] = None
  env: Env = None


SETUP_DATA = {
  'NoneType': lambda data: Data(),
  'str': lambda data: Data(file_path=data),
  'dict': lambda data: Data(**data),
  'Data': lambda data: data,
  'type': lambda data: data,
}


# @error_handler.main
def setup_data(data: Data | dict | str) -> Data:
  data_type = type(data).__name__
  function = SETUP_DATA[data_type]
  return function(data=data)


# @error_handler.main
def case_file_path_is_none(file_path: None = None) -> str:
  module_frame = inspect.stack()[2]
  module_path = module_frame[1]
  return module_path


GET_FILE_PATH = {
  'NoneType': case_file_path_is_none,
  'str': lambda file_path: file_path,
}


# @error_handler.main
def get_file_path(file_path: str | None) -> str:
  _type = type(file_path).__name__
  function = GET_FILE_PATH[_type]
  return function(file_path=file_path)
  

# @error_handler.main
def get_yml_path(file_path: Data) -> str:
  return file_path.replace('.py', '.yml')


FORMAT_ENV_DATA = {
  'NoneType': lambda environment: {},
  'dict': lambda environment: environment,
}


# @error_handler.main
def get_environment_from_yml(yml_path: str) -> dict:
  if path.exists(yml_path) is False:
    return {}

  environment = None
  with open(yml_path, 'r') as file:
    yaml_data = yaml.safe_load(file)
    environment = yaml_data.get('environment')
  # Handle no env vars
  _type = type(environment).__name__
  function = FORMAT_ENV_DATA[_type]
  return function(environment=environment)


# @error_handler.main
def get_variable_from_environment(environment: dict) -> dict:
  for key, value in environment.items():
    if key not in os.environ.keys():
      continue
    environment[key] = os.environ[key]
  return environment


# @error_handler.main
def convert_environment_dict_to_class(environment: dict) -> Env:
  fields = []
  for key, value in environment.items():
    data_classfield = [key, str, dc.field(default=value)]
    fields.append(data_classfield)
  env = dc.make_dataclass(
    'Env',
    fields
  )
  return env()


# @error_handler.main
def main(data: Data | dict | str | None = None) -> Data:
  data = setup_data(data=data)
  data.file_path = get_file_path(file_path=data.file_path)
  data.yml_path = get_yml_path(file_path=data.file_path)
  data.environment = get_environment_from_yml(yml_path=data.yml_path)
  data.environment = get_variable_from_environment(environment=data.environment)
  data.env = convert_environment_dict_to_class(environment=data.environment)
  return data.env


def example() -> None:
  data = [
    Data(
      file_path=__file__.replace('app.py', 'test_resources/app.py'),
    ),
    dict(
      file_path=__file__.replace('app.py', 'test_resources/app.py')
    ),
    '/home/femij/mono_repo/coding_challenges/utils/untested_create_flowchart/create_flowchart_data.py',
    None,
  ]

  store = []
  for d in data:
    d = main(data=d)
    store.append(d)
  
  print(store)


if __name__ == '__main__':
  example()
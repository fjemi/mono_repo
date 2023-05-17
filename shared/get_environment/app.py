#!/usr/bin/env python3

from dataclasses import dataclass, field, make_dataclass
from os import getenv
from os.path import exists
from typing import Dict
import yaml

from api import models
from shared.setup_data import app as setup_data


@dataclass
class Data:
  module_path: str | None = None
  yml_path: str | None = None
  yml_key: str = 'environment'
  yml_data: Dict[str, str] = field(default_factory=lambda: {})
  env: models.Env = field(default_factory=lambda: models.Env())


def get_yml_path(
  module_path: str | None = None,
  yml_path: str | None = None,
) -> str:
  if yml_path:
    return yml_path
  return module_path.replace('.py', '.yml')


def get_yml_data(
  yml_path: str,
  key: str,
) -> dict | None:
  yml_data = {}
  
  # Handle YML file not existing
  if exists(yml_path) is False:
    return yml_data
  
  with open(yml_path, 'r') as file:
    content = file.read()
    data = yaml.safe_load(content)
    # Handle empty YML file
    if data is None:
      return yml_data
    # Handle YML file not having 
    # specified environment key  
    if key not in data.keys():
      return {}
    return data[key]
    
  
def convert_dict_to_dataclass(yml_data: dict) -> models.Env:
  store = []
  for key, value in yml_data.items():
    dataclass_field = (
      key,
      str,
      field(default=value)
    )
    store.append(dataclass_field)
  return make_dataclass('Env', store)()


def get_variables_from_venv(yml_data: dict) -> dict:

  for key in yml_data:
    venv_value = getenv(key)
    if venv_value is None:
      continue
    yml_data[key] = venv_value
  return yml_data


def process_config(
  data: Data | dict | str = None,
  config: Dict | str = None,
) -> Data | dict | str:
  if data is not None:
    return data
  return config['environment']


def main(
  data: Data | dict | str = None,
  # config: dict | str = None,
) -> models.Env:
  # data = process_config(config=config, data=data)
  data = setup_data.main(data=data, data_class=Data)
  data.yml_path = get_yml_path(
    module_path=data.module_path,
    yml_path=data.yml_path,
  )
  data.yml_data = get_yml_data(
    yml_path=data.yml_path,
    key=data.yml_key,
  )
  data.yml_data = get_variables_from_venv(yml_data=data.yml_data)
  data.env = convert_dict_to_dataclass(yml_data=data.yml_data)
  return data.env


def example() -> None:
  data = '''
    yml_path: ${WORKDIR}/utils/get_environment/test_resources/app.yml
  '''
  data = main(data=data)
  print(data)


if __name__ == '__main__':
  example()

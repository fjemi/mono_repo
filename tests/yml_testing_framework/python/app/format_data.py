#!/usr/bin/env python

import json
import yaml
from typing import Any, List, Dict
from pydantic import BaseModel
import dataclasses as dc


@dc.dataclass
class DataClass:
  pass


class Data(BaseModel):
  data: Any | DataClass | dict | str = None
  cast_as: str = 'yml'


def case_dict_as_yml(data: dict) -> str:
  return yaml.dump(
    data=data, 
    indent=2, 
    default_flow_style=None,
  )


def case_str_as_yml(data: str) -> str:
  data = json.loads(data)
  return yaml.dump(
    data=data, 
    indent=2, 
    default_flow_style=None,
  )


def case_basemodel_as_yml(data: BaseModel) -> str:
  data = data.dict()
  return yaml.dump(
    data=data, 
    indent=2, 
    default_flow_style=None,
  )


def case_dataclass_as_yml(data: BaseModel) -> str:
  data = dc.asdict(data)
  return yaml.dump(
    data=data, 
    indent=2, 
    default_flow_style=None,
  )


TYPE_CAST_SWITCHER = {
  "0_yml": case_dict_as_yml,
  "1_yml" : case_str_as_yml,
  "2_yml": case_basemodel_as_yml,
  "3_yml": case_dataclass_as_yml,
}


def case_data_is_str(data: str) -> Data:
  return  Data(data=data)


def case_data_is_dict(data: dict) -> Data:
  print(Data(**data))
  return Data(**data)


def case_data_is_basemodel(data: Data) -> Data:
  return data


SETUP_SWITCHER = {
  'Data': case_data_is_basemodel,
  'dict': case_data_is_dict,
  'str': case_data_is_str,
}


def setup(data: Data | dict):
  case = type(data).__name__
  function = SETUP_SWITCHER[case]
  return function(data=data)


def main(data: Data | dict) -> Any:
  data = setup(data)
  _type = type(data.data)
  conditions = [
    _type.__name__ == 'dict',
    _type.__name__ == 'str',
    hasattr(data.data, '_fields__'),
    hasattr(data.data, '__dataclassfields__'),
  ]
  condition_index = conditions.index(1)
  case = f'{condition_index}_{data.cast_as}'
  function = TYPE_CAST_SWITCHER[case]
  return function(data=data.data)


#!/usr/bin/env python3

import dataclasses as dc
from typing import Dict

from shared.format_request_attributes import app as format_request_attributes


@dc.dataclass
class DataClass:
  # General dataclass type hint
  ...


async def format_arguments_from_api_call(
  _locals: dict,
  data_classes: Dict[str, DataClass],
  main_data_class: DataClass,
) -> DataClass:
  request = _locals['request']
  data = await format_request_attributes.main(
    request=request,
    data_classes=data_classes,
    main_data_class=main_data_class,
  )
  return data


async def format_arguments_from_module_call(
  _locals: dict,
  data_classes: Dict[str, DataClass],
  main_data_class: DataClass,
) -> DataClass:
  store = {}
  for name, dataclass in data_classes.items():
    dataclass = dataclass()
    for field in dc.fields(dataclass):
      if field.name not in _locals:
        continue
      value = _locals[field.name]
      if value is None:
        continue
      setattr(dataclass, field.name, value)
    store[name] = dataclass
  data = main_data_class(**store)
  return data


FORMAT_MAIN_ARGUMENTS = {
  'api': format_arguments_from_api_call,
  'module': format_arguments_from_module_call, 
}


async def main(
  _locals: dict,
  data_classes: Dict[str, DataClass] | None = None,
  main_data_class: DataClass | None = None,
) -> 'Data':
  call_method = 'api' if _locals['request'] else 'module'
  switcher = FORMAT_MAIN_ARGUMENTS[call_method]
  data = await switcher(
    _locals=_locals,
    data_classes=data_classes,
    main_data_class=main_data_class,
  )
  data.call_method = call_method
  return data

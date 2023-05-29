# #!/usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import Dict, List

from api import models as api_models


@dataclass
class Body:
  grid: List[List[int]] | Dict[str, str] | str | None = None
  convert_to: str | None = None


@dataclass
class Data:
  body: Body | None = None
  request: bool = False
  result: List[List[int]] | Dict[str, str] | None = None


async def process_request_args(_locals: dict) -> Data:
  request = _locals['request']
  body = Body(**asdict(request.data.body))
  data = Data(body=body, request=True)
  return data


async def process_non_request_args(_locals: dict) -> Data:
  del _locals['request']
  body = Body(**_locals)
  data = Data(body=body)
  return data


PROCESS_MAIN_ARGS = {
  'non_request': process_non_request_args,
  'request': process_request_args,
}


async def process_main_args(_locals: dict) -> Data:
  cases = [
    int(_locals['request'] is not None) * 'request',
    int(_locals['request'] is None) * 'non_request',
  ]
  cases = ''.join(cases)
  switcher = PROCESS_MAIN_ARGS[cases]
  data = await switcher(_locals=_locals)
  return data


async def convert_grid_dict_to_list(data: Data) -> Data:
  grid_list = []

  row = 0
  store = []
  for key, value in data.body.grid.items():
    a = int(key.split('.')[0])
    if a != row:
      grid_list.append(store)
      store = []
      row = a
    store.append(value)
  grid_list.append(store)

  data.result = grid_list
  return data


async def convert_grid_list_to_dict(data: Data) -> Data:
  grid_dict = {}
  n = len(data.body.grid)
  m = len(data.body.grid[0])

  for i in range(n):
    for j in range(m):
      position = f'{i}.{j}'
      value = data.body.grid[i][j]
      grid_dict[position] = value

  data.result = grid_dict
  return data


async def convert_grid_list_to_str(data: Data) -> Data:
  grid_str = ''
  m = len(data.body.grid)
  n = len(data.body.grid[0])

  for i in range(m):
    for j in range(n):
      position = f'{i}.{j}'
      value = data.body.grid[i][j]
      string = f'|{position},{value}'
      grid_str = grid_str + string

  grid_str = grid_str[1:]
  data.result = grid_str
  return data


async def convert_grid_dict_to_str(data: Data) -> Data:
  grid_str = ''
  for position, value in data.body.grid.items():
    string = f'|{position},{value}'
    grid_str = grid_str + string
  grid_str = grid_str[1:]
  data.result = grid_str
  return data


async def convert_grid_str_to_dict(data: Data) -> Data:
  items = data.body.grid.split('|')
  store = {}
  for item in items:
    key, value = item.split(',')
    store[key] = value
  data.result = store
  return data


async def convert_grid_str_to_list(data: Data) -> Data:
  store = []
  row = []
  n = '0'

  grid = data.body.grid.split('|')
  for cell in grid:
    position, value = cell.split(',')
    index = position.split('.')[0]

    if n != index:
      store.append(row)
      row = []
      n = index

    row.append(value)
  # Get last row
  store.append(row)

  data.result = store
  return data


MAKE_CONVERSION = {
  'dict.list': convert_grid_dict_to_list,
  'list.dict': convert_grid_list_to_dict,
  'list.str': convert_grid_list_to_str,
  'dict.str': convert_grid_dict_to_str,
  'str.dict': convert_grid_str_to_dict,
  'str.list': convert_grid_str_to_list, 
}


async def make_conversion(data: Data) -> Data:
  grid_type = type(data.body.grid).__name__
  cases = f'{grid_type}.{data.body.convert_to}'
  switcher = MAKE_CONVERSION[cases]
  data = await switcher(data=data)
  return data


async def get_response(data: Data) -> dict | list | str:
  if not data.request:
    return data.result
  data = {'grid': data.result}
  return data


# pylint: disable=unused-argument
async def main(
  request: api_models.Request | None = None,
  grid: List[List[int]] |  Dict[str, int] | str | None = None,
  convert_to: str | None = None
) -> dict | list | str:
  data = await process_main_args(_locals=locals())
  data = await make_conversion(data=data)
  data = await get_response(data=data)
  return data

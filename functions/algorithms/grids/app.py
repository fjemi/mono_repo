# #!/usr/bin/env python3

import dataclasses as dc
from typing import Dict, List
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  grid: List[List[int]] | Dict[str, str] | str | None = None
  convert_to: str | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  call_method: str = 'api'
  response: List[List[int]] | Dict[str, str] | None = None


async def convert_grid_dict_to_list(data: Data) -> list:
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
  return grid_list


async def convert_grid_list_to_dict(data: Data) -> dict:
  grid_dict = {}
  n = len(data.body.grid)
  m = len(data.body.grid[0])

  for i in range(n):
    for j in range(m):
      position = f'{i}.{j}'
      value = data.body.grid[i][j]
      grid_dict[position] = value
  return grid_dict


async def convert_grid_list_to_str(data: Data) -> str:
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
  return grid_str


async def convert_grid_dict_to_str(data: Data) -> str:
  grid_str = ''
  for position, value in data.body.grid.items():
    string = f'|{position},{value}'
    grid_str = grid_str + string
  grid_str = grid_str[1:]
  return grid_str


async def convert_grid_str_to_dict(data: Data) -> dict:
  items = data.body.grid.split('|')
  store = {}
  for item in items:
    key, value = item.split(',')
    store[key] = value
  return store


async def convert_grid_str_to_list(data: Data) -> list:
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
  return store


MAKE_CONVERSION = {
  'dict.list': convert_grid_dict_to_list,
  'list.dict': convert_grid_list_to_dict,
  'list.str': convert_grid_list_to_str,
  'dict.str': convert_grid_dict_to_str,
  'str.dict': convert_grid_str_to_dict,
  'str.list': convert_grid_str_to_list, 
}


async def make_conversion(data: Data) -> dict | list | str:
  grid_type = type(data.body.grid).__name__
  cases = f'{grid_type}.{data.body.convert_to}'
  switcher = MAKE_CONVERSION[cases]
  data = await switcher(data=data)
  return data


async def get_response(data: Data) -> dict | list | str:
  if data.call_method == 'module':
    return data.response
  data = {'grid': data.response}
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  grid: List[List[int]] |  Dict[str, int] | str | None = None,
  convert_to: str | None = None
) -> dict | list | str:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  data.response = await make_conversion(data=data)
  data = await get_response(data=data)
  return data

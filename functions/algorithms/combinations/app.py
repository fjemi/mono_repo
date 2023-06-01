#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Any
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  items: List[Any] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  combinations: List[List] | None = dc.field(default_factory=lambda: [])
  positions: List[List] | None = dc.field(default_factory=lambda: [])
  return_positions: bool = False
  values: List[List[Any]] | None = None
  call_method: str = 'module'


async def set_combinations_and_positions(data: Data) -> Data:
  positions = []

  for i in range(len(data.body.items)):
    data.positions.append([i])
    positions.append(i)

  data.positions.append(positions)
  data.combinations.append(positions)
  return data


async def get_combinations(data: Data) -> Data:
  n = len(data.body.items)
  if n >= 3:
    n = n - 2
  for k in range(n):
    store = []
    for item_i in data.combinations[0]:
      for item_j in data.combinations[-1]:
        # Format item as list if needed
        if not isinstance(item_j, list):
          item_j = [item_j]
        # Handle duplicate positions within a combination
        if item_i in item_j or item_i == item_j:
          continue
        # Create the combination
        combination = item_j + [item_i]
        combination.sort()
        # Ignore combinations that have already been added -> (1, 2) and (2, 1)
        if combination in store:
          continue
        store.append(combination)
    data.positions = data.positions + store
    data.combinations.append(store)
  return data


async def get_combination_values(data: Data) -> List:
  '''Returns values associated with combinations of positions'''
  store = []
  # Get the value associated with each position in a combination
  for position in data.positions:
    combination = []
    for i in position:
      value = data.body.items[i]
      combination.append(value)
    store.append(combination)
  data.values = store
  return store


async def get_response(data: Data) -> dict:
  if data.call_method == 'api':
    return {'combinations': data.combinations}
  if data.call_method == 'module':
    return data.combinations


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  items: List[Any] | None = None,
) -> Data:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await set_combinations_and_positions(data=data)
  data = await get_combinations(data=data)

  if data.return_positions is True:
    return data.positions

  data.values = await get_combination_values(data=data)
  data = await get_response(data=data)
  return data


async def example() -> None:
  items = ['a', 'b', 'c']
  result = await main(items=items)
  print(result)


if __name__ == '__main__':
  import asyncio


  asyncio.run(example())

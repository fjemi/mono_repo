#!/usr/bin/env python3

import dataclasses as dc
from typing import Dict, List
import random

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Counts:
  positions: int = 0
  mines: int = 0


@dc.dataclass
class Data:
  m: int = 12
  n: int = 12
  mine_density: float = .2
  mine_locations: List[str] | None = None
  grid: Dict[str, str] | None = None
  user_id: str = 'user_id'


async def process_args(_locals: dict) -> Data:
  data = Data()
  for field in dc.fields(data):
    if field.name not in locals():
      continue
    value = locals()[field.name]
    if not value:
      continue
    setattr(data, field.name, value)
  return data


async def get_grid(data: Data) -> Data:
  grid = {}
  for i in range(data.m):
    for j in range(data.n):
      position = f'{i}.{j}'
      grid[position] = ''
  data.grid = grid
  return data


async def get_mine_locations(data: Data) -> Data:
  counts = Counts()
  counts.positions = (data.m + 1) * (data.n + 1)
  counts.mines = int(counts.positions * data.mine_density)

  positions = list(data.grid.keys())
  store = []
  while len(store) < counts.mines:
    position = random.choice(positions)
    if position in store:
      continue
    store.append(position)
    data.grid[position] = 'mine'

  data.mine_locations = store
  return data


async def get_neighboring_mine_counts(data: Data) -> Data:
  for position, value in data.grid.items():
    mines = []
    if value == 'mine':
      continue

    i, j = position.split('.')
    i, j = int(i), int(j)

    for a in range(i - 1, i + 2):
      for b in range(j - 1, j + 2):
        outside_bounds = [
          a < 0,
          b < 0,
          a >= data.m,
          b >= data.n,
          [i, j] == [a, b],
        ]
        if sum(outside_bounds) != 0:
          continue

        neighbor = f'{a}.{b}'
        value = data.grid[neighbor]
        mines.append(value)
    count = mines.count('mine')
    data.grid[position] = count

  return data


async def main(
  m: int | None = None,
  n: int | None = None,
  mine_density: float | None = None,
  user_id: str | None = None,
) -> Dict[str, str]:
  data = await process_args(_locals=locals())
  data = await get_grid(data=data)
  data = await get_mine_locations(data=data)
  data = await get_neighboring_mine_counts(data=data)
  return data


async def example() -> None:
  result = await main(m=4, n=4)
  print(result)


if __name__ == '__main__':
  import asyncio


  result = asyncio.run(example())

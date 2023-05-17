#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List, Dict
from copy import deepcopy
import yaml

from api import models


# Increment position to step to adjacencies
ADJACENT_STEPS = [
  [0, 1],
  [1, 0],
  [0, -1],
  [-1, 0],
]


@dataclass 
class Body(models.Body):
  grid: List[List[int]] | None = None


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None


@dataclass
class ModuleData:
  body: Body | None = None
  positions: Dict[str, int] | None = None
  adjacencies: Dict[str, List[str]] | None = None
  steps: List[List[int]] = field(default_factory=lambda: ADJACENT_STEPS)
  islands: Dict[str, List[str]] | None = None
  output: int | None = None


async def get_positions(grid: List[List[int]]) -> Dict[str, int]:
  grid_m = range(len(grid))
  grid_n = range(len(grid[0]))

  positions = {}
  for i in grid_m:
    for j in grid_n:
      key = f'{i}.{j}'
      value = grid[i][j]
      # Exclude positions that are water
      if value == 0:
        continue
      positions[key] = value
  return positions


async def get_adjacent_positions(
  position: str,
  positions: Dict[str, int],
  steps: List[List[int]],
) -> List[str]:
  a, b = position.split('.')
  a = int(a)
  b = int(b)

  store = [position]
  for step in steps:
    c = a + step[0]
    d = b + step[1]
    adjacent_position = f'{c}.{d}'
    # Only add adjacent positions with a value of 1
    exclude_condition = None
    try:
      exclude_condition = positions[adjacent_position] == 0
    except KeyError:
      exclude_condition = True
    if exclude_condition is True:
      continue
    store.append(adjacent_position)
  return store


async def get_adjacencies(
  positions: Dict[str, int],
  steps: List[List[int]],
) -> Dict[str, List[str]]:
  adjacent_positions = {}
  keys = list(positions.keys())
  keys_n = range(len(keys))
  for i in keys_n:
    key = keys[i]
    adjacent_positions[key] = await get_adjacent_positions(
      position=key,
      steps=steps,
      positions=positions,
    )
  return adjacent_positions


async def store_indirect_adjacencies(
  store: List[str],
  adjacencies: List[str],
  adjacent_positions: Dict[str, List[str]],
) -> Dict[str, List[str]]:
  for adjacent_position in adjacent_positions:
    indirect_adjacencies = adjacencies[adjacent_position]
    indirect_adjacencies_range = range(len(indirect_adjacencies))
    for i in indirect_adjacencies_range:
      indirect_adjacency = indirect_adjacencies[i]
      if indirect_adjacency in store:
        continue
      store.append(indirect_adjacency)
  return store


async def get_islands_from_direct_and_indirect_adjacencies(
  adjacencies: Dict[str, List[str]],
) -> Dict[str, List[str]]:
  for position, adjacent_positions in reversed(adjacencies.items()):
    store = [position]
    store = await store_indirect_adjacencies(
      store=store,
      adjacencies=adjacencies,
      adjacent_positions=adjacent_positions,
    )
    adjacencies[position] = store
  return adjacencies


async def get_unique_islands(
  islands: Dict[str, List[str]],
) -> Dict[str, List[str]]:
  islands_copy = deepcopy(islands)
  for key in islands:
    island = islands[key]
    if key not in islands_copy:
      continue
    for position in island:
      conditions = [
        position == key,
        position not in islands_copy,
      ]
      if True in conditions:
        continue
      del islands_copy[position]
  return islands_copy


async def get_response(data: ModuleData) -> models.Response:
  islands = list(data.islands.values())
  data = f'''
    input: {asdict(data.body)}
    output: 
      islands: 
        n: {data.output}
        values: {islands}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = ModuleData(body=request.data.body)
  request = None
  data.positions = await get_positions(grid=data.body.grid)
  data.adjacencies = await get_adjacencies(
    positions=data.positions,
    steps=data.steps,
  )
  data.islands = await get_islands_from_direct_and_indirect_adjacencies(
    adjacencies=data.adjacencies)
  data.islands = await get_unique_islands(islands=data.islands)
  data.output = len(data.islands)
  data = await get_response(data=data)
  return data

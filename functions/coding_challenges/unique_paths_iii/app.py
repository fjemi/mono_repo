#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


NEIGHBOR_STEPS = [
  [-1, 0],
  [0, -1],
  [1, 0],
  [0, 1],
]


@dc.dataclass
class Body:
  grid: List[List[int]] | None = None


@dc.dataclass
class Shape:
  n: int = 0
  m: int = 0


@dc.dataclass
class Positions:
  neighbors: Dict[str, List[List[int]]] | None = None
  obstacles: List[List[int]] | None = None
  start: List[int] | None = None
  end: List[int] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  paths: List[List[int]] = dc.field(default_factory=lambda: [])
  shape: Shape | None = None
  positions: Positions | None = None
  neighbor_steps: List[List[int]] = dc.field(
    default_factory=lambda: NEIGHBOR_STEPS)
  output: int = 0


async def get_shape(grid: List[List[int]]) -> Shape:
  shape = Shape(
    m=len(grid),
    n=len(grid[0]),
  )
  return shape


async def get_neighbors(
  grid: List[List[int]],
  position: List[int],
  shape: Shape,
  neighbor_steps: List[List[int]],
  neighbors: Dict[str, List[str]],
) -> Data:
  store = []
  for step in neighbor_steps:
    i = position[0] + step[0]
    j = position[1] + step[1]

    conditions = [
      i < 0,
      j < 0,
      i >= shape.m,
      j >= shape.n,
    ]
    if True in conditions:
      continue

    value = grid[i][j]
    if value == -1:
      continue
    neighbor = f'{i}.{j}'
    store.append(neighbor)
  position = f'{position[0]}.{position[1]}'
  neighbors[position] = store
  return neighbors


async def get_positions(
  grid: List[List[int]],
  shape: Shape,
  neighbor_steps: List[List[int]],
) -> Positions:
  obstacles = []
  neighbors = {}
  start = None
  end = None

  for i in range(shape.m):
    for j in range(shape.n):
      position = f'{i}.{j}'
      value = grid[i][j]
      if value == -1:
        obstacles.append(position)
        continue
      if value == 1:
        start = position
      if value == 2:
        end = position
        # neighbors[position] = []
        continue
      neighbors = await get_neighbors(
        grid=grid,
        position=[i, j],
        shape=shape,
        neighbor_steps=neighbor_steps,
        neighbors=neighbors,
      )

  positions = Positions(
    neighbors=neighbors,
    obstacles=obstacles,
    start=start,
    end=end,
  )
  return positions


async def get_paths(positions: Positions) -> List[List[str]]:
  paths = [[positions.start]]
  while len(paths[-1]) != 0:
    store = []
    for path in paths[-1]:
      branch = path.split('|')
      leaf = branch[-1]
      if leaf == positions.end:
        continue
      neighbors = positions.neighbors[leaf]
      for neighbor in neighbors:
        conditions = [
          neighbor in branch,
          neighbor in positions.obstacles,
        ]
        if True in conditions:
          continue

        next_branch = branch + [neighbor]
        next_branch = '|'.join(next_branch)
        store.append(next_branch)
    paths.append(store)
  return paths


async def process_paths(
  paths: List[List],
  end: str,
  obstacles: List[str],
  shape: Shape,
) -> List[str]:
  store = []
  paths_range = range(len(paths))
  available_positions_n = shape.m * shape.n - len(obstacles)
  for i in paths_range:
    for path in paths[i]:
      index = path.rfind('|') + 1
      path_end = path[index:]

      path_as_list = path.split('|')
      path_end = path_as_list[-1]

      conditions = [
        path_end == end,
        path not in store,
        len(path_as_list) == available_positions_n,
      ]
      if sum(conditions) / len(conditions) != 1:
        continue

      store.append(path)
  return store


async def get_response(data: Data) -> dict:
  data = {
    'count': data.output,
    'paths': data.paths,
  }
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  grid: List[List[int]] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  data.shape = await get_shape(grid=data.body.grid)
  data.positions = await get_positions(
    grid=data.body.grid,
    shape=data.shape,
    neighbor_steps=data.neighbor_steps,
  )
  data.paths = await get_paths(positions=data.positions)
  data.paths = await process_paths(
    paths=data.paths,
    end=data.positions.end,
    shape=data.shape,
    obstacles=data.positions.obstacles,
  )
  data.output = len(data.paths)
  data = await get_response(data=data)
  return data

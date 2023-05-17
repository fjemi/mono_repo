#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict
import yaml

from api import models


NEIGHBOOR_STEPS = [
  [-1, 0],
  [0, -1],
  [1, 0],
  [0, 1],
]


@dataclass 
class Body(models.Body):
  string: str = ''
  word_dict: List[str] = field(default_factory=lambda: [])


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None


@dataclass
class Shape:
  n: int = 0
  m: int = 0


@dataclass
class Positions:
  neighboors: Dict[str, List[List[int]]] | None = None
  obstacles: List[List[int]] | None = None
  start: List[int] | None = None
  end: List[int] | None = None


@dataclass
class ModuleData:
  body: Body | None = None
  paths: List[List[int]] = field(default_factory=lambda: [])
  shape: Shape | None = None
  positions: Positions | None = None
  neighboor_steps: List[List[int]] = field(
    default_factory=lambda: NEIGHBOOR_STEPS)
  output: int = 0


async def get_shape(grid: List[List[int]]) -> Shape:
  shape = Shape(
    m=len(grid),
    n=len(grid[0]),
  )
  return shape


async def get_neighboors(
  grid: List[List[int]],
  position: List[int],
  shape: Shape,
  neighboor_steps: List[List[int]],
  neighboors: Dict[str, List[str]],
) -> ModuleData:
  store = []
  for step in neighboor_steps:
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
    neighboor = f'{i}.{j}'
    store.append(neighboor)
  position = f'{position[0]}.{position[1]}'
  neighboors[position] = store
  return neighboors


async def get_positions(
  grid: List[List[int]],
  shape: Shape,
  neighboor_steps: List[List[int]],
) -> Positions:
  obstacles = []
  neighboors = {}
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
        # neighboors[position] = []
        continue
      neighboors = await get_neighboors(
        grid=grid,
        position=[i, j],
        shape=shape,
        neighboor_steps=neighboor_steps,
        neighboors=neighboors,
      )

  positions = Positions(
    neighboors=neighboors,
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
      neighboors = positions.neighboors[leaf]
      for neighboor in neighboors:
        conditions = [
          neighboor in branch,
          neighboor in positions.obstacles,
        ]
        if True in conditions:
          continue

        next_branch = branch + [neighboor]
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


async def get_response(data: ModuleData) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      paths:
        n: {data.output}
        values: {data.paths}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = ModuleData(body=request.data.body)
  data.shape = await get_shape(grid=data.body.grid)
  data.positions = await get_positions(
    grid=data.body.grid,
    shape=data.shape,
    neighboor_steps=data.neighboor_steps,
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

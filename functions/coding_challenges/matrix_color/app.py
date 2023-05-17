#!/usr/bin/env python3

from typing import List, Dict, Any
from dataclasses import dataclass, field, fields, asdict
from copy import deepcopy
import yaml

from api import models


@dataclass
class Body(models.Body):
  matrix: List[List[Any]] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Shape:
  m: int = 0
  n: int = 0


@dataclass
class Neighbors:
  matching: Dict[str, List[str]] | None = None
  expanded: Dict[str, List[str]] | None = None


@dataclass
class Data:
  body: Body | None = None
  shape: Shape | None = None
  neighbors: Neighbors | None = None

  matching_adjacent_positions: Dict[str, List[str]] = field(
    default_factory=lambda: {})
  expanded_adjacent_positions: Dict[str, List[str]] = field(
    default_factory=lambda: {})
  adjacent_positions_count: int = 0


async def get_shape(matrix: List[List[str]]) -> Shape:
  shape = Shape
  shape.m = len(matrix)
  shape.n = len(matrix[0])
  return shape


# TODO: Update to neighbors from adjacent positions
# async def get_neighbors(data: Data) -> Neighbors:
#   neighbors = Neighbors()

#   return neighbors


async def get_current_positions_adjacent_positions(
  i: int, 
  j: int,
  current_value: Any,
  data: Data,
) -> Dict[str, List[str]]:
  current_position = f'{i}.{j}'
  store = []
  for k in range(i - 1, i + 2):
    # Exceeds bounds
    if k >= data.shape.m or k < 0:
      continue
    for l in range(j - 1, j + 2):
      # Exceeds bounds
      if l >= data.shape.n or l < 0:
        continue
      position = f'{k}.{l}'
      # Ignore current position
      if position == current_position:
        continue

      value = data.body.matrix[k][l]
      if current_value != value:
        continue

      store.append(position)
  return {current_position: store}


async def get_matching_adjacent_positions(data: Data) -> Dict[str, List[str]]:
  store = {}
  for i in range(data.shape.m):
    for j in range(data.shape.n):
      current_value = data.body.matrix[i][j]
      adjacent_positions = await get_current_positions_adjacent_positions(
        i=i,
        j=j,
        current_value=current_value,
        data=data,
      )
      store.update(adjacent_positions)
  return store


async def merge_adjacent_and_semi_adjacent_values(
  adjacent_values: List[int],
  semi_adjacent_values: List[int],
) -> List[int]:
  for value in semi_adjacent_values:
    if value in adjacent_values:
      continue
    adjacent_values.append(value)
  return adjacent_values


async def get_expanded_adjacent_positions(
  matching_adjacent_positions: Dict[str, List[str]],
) -> List[List[str]]:
  store = deepcopy(matching_adjacent_positions)
  for key, values in reversed(store.items()):
    values.append(key)
    for value in values:
      semi_adjacent_values = store[value]
      store[key] = await merge_adjacent_and_semi_adjacent_values(
        adjacent_values=values,
        semi_adjacent_values=semi_adjacent_values,
      )
      store[key].sort()
  return list(store.values())


async def remove_duplicate_adjacent_positions(
  expanded_adjacent_positions: List[List[str]],
) -> List[List[str]]:
  store = []
  n = len(expanded_adjacent_positions)
  for i in range(n):
    if expanded_adjacent_positions[i] in store:
      continue
    store.append(expanded_adjacent_positions[i])
  return store


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      connections:
        values: {data.expanded_adjacent_positions}
        n: {data.adjacent_positions_count}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  body = Body(**asdict(request.data.body))
  data = Data(body=body)
  request = None
  data.shape = await get_shape(matrix=data.body.matrix)
  # data.neighbors = await get_neighbors(data=data)

  data.matching_adjacent_positions = await get_matching_adjacent_positions(data=data)
  data.expanded_adjacent_positions = await get_expanded_adjacent_positions(
    matching_adjacent_positions=data.matching_adjacent_positions)
  data.expanded_adjacent_positions = await remove_duplicate_adjacent_positions(
    expanded_adjacent_positions=data.expanded_adjacent_positions)
  data.adjacent_positions_count = len(data.expanded_adjacent_positions)

  data = await get_response(data=data)
  return data

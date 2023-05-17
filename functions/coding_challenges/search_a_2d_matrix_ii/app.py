#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List
import yaml

from shared.partition_matrix_into_edges import app as partition_matrix_into_edges
from api import models


@dataclass 
class Body(models.Body):
  matrix: List[List[int]] | None = None
  target: int | None = None


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None


@dataclass
class ModuleData:
  body: Body | None = None
  target_position: List[str | int] | None = None
  edges: List[List[str]] = field(default_factory=lambda: [])


async def find_target_at_corners(
  target: int,
  edge: List[str],
  values: List[int],
  matrix: List[List[int]],
) -> str:
  _ = matrix

  values_n = range(len(values))
  for i in values_n:
    if target != values[i]:
      continue
    return edge[i]


async def find_target_between_corners(
  target: int,
  edge: List[str],
  values: List[int],
  matrix: List[List[int]],
) -> None | List[int]:
  _ = values

  direction = {
    edge[0][0] == edge[1][0]: 1,  # right
    edge[0][0] != edge[1][0]: 0,  # down
  }
  direction = direction[1]
  n = abs(edge[0][direction] - edge[1][direction])
  n = range(1, n)

  next_edge = None
  for i in n:
    next_edge = edge[0]
    next_edge[direction] += i
    a, b = next_edge
    value = matrix[a][b]
    if value == target:
      break
  return next_edge


async def target_not_in_edge(
  target: int,
  edge: List[str],
  values: List[int],
  matrix: List[List[int]],
) -> None:
  _ = target, edge, values, matrix


FIND_TARGET_POSITION = {
  0: find_target_at_corners,
  1: find_target_between_corners,
  2: target_not_in_edge,
}


async def find_target_position(data: ModuleData) -> ModuleData:
  edges_n = len(data.edges)
  for i in range(edges_n):
    edge = data.edges[i]

    a, b = edge[0]
    value_1 = data.body.matrix[a][b]
    c, d = edge[1]
    value_2 = data.body.matrix[c][d]
    values = [value_1, value_2]

    cases = [
      data.body.target in values,
      values[0] < data.body.target and data.body.target < values[1],
      data.body.target not in values,
    ]
    _case = cases.index(1)
    function = FIND_TARGET_POSITION[_case]
    data.target_position = await function(
      target=data.body.target,
      edge=edge,
      matrix=data.body.matrix,
      values=values,
    )
    if data.target_position is not None:
      break
  return data


async def get_response(data: ModuleData) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      target_position: {data.target_position}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = ModuleData(body=request.data.body)
  request = None
  m = len(data.body.matrix)
  n = len(data.body.matrix[0])
  data.edges = partition_matrix_into_edges.main(f'shape: [{m}, {n}]')
  data = await find_target_position(data=data)
  data = await get_response(data=data)
  return data

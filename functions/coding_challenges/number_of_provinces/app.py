#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from copy import deepcopy
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


# Step to neighboring positions
STEPS = {
  'main': [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
  ],
  'diagonal': [
    (-1, -1),
    (1, 1),
    (1, -1),
    (-1, 1),
  ],
}


@dc.dataclass
class Body:
  cities: List[List[int]] | None = None
  exclude_diagonals: bool = False


@dc.dataclass
class Steps:
  horizontal: List[List[int]]
  vertical: List[List[int]]
  diagonal: List[List[int]]


@dc.dataclass
class Shape:
  m: int = 0
  n: int = 0


@dc.dataclass
class Connections:
  direct: Dict[str, List[str]] | None = None
  indirect: Dict[str, List[str]] | None = None


@dc.dataclass
class Provinces:
  values: List[List[str]] | None = None
  n: int = 0


@dc.dataclass
class Data:
  body: Body | None = None
  steps: Dict[str, List[List[int]]] | List[List[int]] = dc.field(
    default_factory=lambda: STEPS)
  shape: Shape | None = None
  connections: Connections | None = None
  provinces: Provinces | None = None


async def format_steps(
  steps: Dict[str, List[List[int]]],
  exclude_diagonals: bool,
) -> List[List[int]]:
  if exclude_diagonals:
    return steps['main']
  if not exclude_diagonals:
    steps = steps['main'] + steps['diagonal']
    return steps


async def get_shape(cities: List[List[int]]) -> Shape:
  shape = Shape(
    m=len(cities),
    n=len(cities[0])
  )
  return shape


async def get_neighbors(
  cities: List[List[int]],
  position: List[int],
  steps: List[List[int]],
  shape: Shape,
) -> List[str]:
  store = []
  position_value = cities[position[0]][position[1]]
  if position_value != 1:
    return store

  store.append('.'.join([str(x) for x in position]))

  for step in steps:
    a = position[0] + step[0]
    b = position[1] + step[1]
    position_value = cities[position[0]][position[1]]

    bounds_conditions = [
      a < 0,
      b < 0,
      a >= shape.m,
      b >= shape.n,
      position_value != 1,
    ]
    if True in bounds_conditions:
      continue

    value = cities[a][b]
    if value != 1:
      continue

    neighbor = f'{a}.{b}'
    store.append(neighbor)

  return store


async def get_direct_connections(
  cities: List[List[int]],
  steps: List[List[int]],
  shape: Shape,
) -> Dict[str, List[str]]:
  store = {}
  for i in range(shape.m):
    for j in range(shape.n):
      position = [i, j]
      neighbors = await get_neighbors(
        position=position,
        steps=steps,
        cities=cities,
        shape=shape,
      )
      position = '.'.join([str(x) for x in position])
      store[position] = neighbors
  return store


async def get_indirect_connections(
  direct_connections: Dict[str, List[str]]
) -> Dict[str, List[str]]:
  connections = deepcopy(direct_connections)
  for position, neighbors in connections.items():
    if not neighbors:
      continue
    for neighbor in neighbors:
      indirect_connections = connections[neighbor]
      for indirect_neighbor in indirect_connections:
        if indirect_neighbor in neighbors:
          continue
        neighbors.append(indirect_neighbor)
    connections[position] = neighbors
  return connections


async def get_connections(data: Data) -> Connections:
  connections = Connections()
  connections.direct = await get_direct_connections(
    cities=data.body.cities,
    steps=data.steps,
    shape=data.shape,
  )
  connections.indirect = await get_indirect_connections(
    direct_connections=connections.direct
  )
  return connections


async def get_provinces(
  indirect_connections: Dict,
) -> List[List[int]]:
  store = []
  for key, value in indirect_connections.items():
    _ = key
    value.sort()
    if value in store:
      continue
    store.append(value)

  store.sort()
  n = len(store) - 1
  provinces = Provinces(values=store, n=n)
  return provinces


async def get_response(data: Data) -> dict:
  return {
    'provinces': data.provinces.values,
    'count': data.provinces.n,
  }


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  cities: List[List[int]] | None = None,
  exclude_diagonals: bool | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.steps = await format_steps(
    steps=data.steps,
    exclude_diagonals=data.body.exclude_diagonals,
  )
  data.shape = await get_shape(cities=data.body.cities)
  data.connections = await get_connections(data=data)
  data.provinces = await get_provinces(
    indirect_connections=data.connections.indirect,
  )
  data = await get_response(data=data)
  return data

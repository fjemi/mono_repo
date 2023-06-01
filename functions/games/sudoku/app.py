# #!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from copy import deepcopy
from math import sqrt, floor
import os
import sys
from fastapi import Request

from functions.algorithms.grids import app as grid_algorithms
from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  grid: List[List[int | str]] | None = None


@dc.dataclass
class Group:
  positions: Dict[str, int] | List[List[int]] | None = None
  values: Dict[str, List[int]] | List[List[int]] | None = None
  available_values: Dict[str, List[int]] | List[List[int]] | None = None
  scores: Dict[str, float] | None = None


@dc.dataclass
class Groups:
  n: int = 0
  grid: Dict[str, int] | None = None
  sub_grids: Group = dc.field(default_factory=lambda: Group())
  rows: Group = dc.field(default_factory=lambda: Group())
  columns: Group = dc.field(default_factory=lambda: Group())
  intersections: Group = dc.field(default_factory=lambda: Group())
  values: Dict[str, float] | None = None


@dc.dataclass
class Iterations:
  count: int = 0
  maximum: int = 1400


@dc.dataclass
class Data:
  body: Body | None = None
  call_method: str = 'api'
  n: int = 0
  groups: Groups | None = None
  tree: List[List[Dict[str, int]]] | None = None
  values_total: int = 0
  solution: Dict | List | None = None
  iterations: Iterations = dc.field(default_factory=lambda: Iterations())


async def get_values_total(n: int) -> int:
  store = 0
  _range = range(1, n + 1)
  for i in _range:
    store += i * n
  return store


async def get_intersection_positions(n: int) -> Dict[str, List[str]]:
  store = {}
  _range = range(n)
  for i in _range:
    for j in _range:
      position = f'{i}.{j}'
      store[position] = []
      for k in _range:
        neighbor = f'{i}.{k}'
        store[position].append(neighbor)
        neighbor = f'{k}.{j}'
        if neighbor != position:
          store[position].append(neighbor)
  return store


async def get_row_positions(n: int) -> List[List[str]]:
  store = {}
  _range = range(n)
  for i in _range:
    store[i] = []
    for j in _range:
      position = f'{i}.{j}'
      store[i].append(position)
  return list(store.values())


async def get_column_positions(n: int) -> List[List[str]]:
  _range = range(n)
  store = {}

  for i in _range:
    store[i] = []
    for j in _range:
      position = f'{j}.{i}'
      store[i].append(position)
  return store


async def get_groups(
  n: int,
  grid: Dict | None = None,
) -> Groups:
  store = Groups(n=n, grid=grid)
  store.intersections.positions = await get_intersection_positions(n=n)
  store.rows.positions = await get_row_positions(n=n)
  store.columns.positions = await get_column_positions(n=n)
  return store


async def get_grid_values(
  grid: Dict[str, int],
  n: int,
) -> Dict[int, float]:
  store = {}
  values = list(grid.values())
  for i in range(1, n + 1):
    count = values.count(i)
    percent = round(count / n, 2)
    store[i] = percent
  return store


async def get_row_values(groups: Groups) -> List[List[int]]:
  values = []
  for i in range(groups.n):
    row = groups.rows.positions[i]
    store = []
    for position in row:
      value = groups.grid[position]
      store.append(value)
    values.append(store)
  return values


async def get_column_values(groups: Groups) -> List[List[int]]:
  values = []
  for i in range(groups.n):
    row = groups.columns.positions[i]
    store = []
    for position in row:
      value = groups.grid[position]
      store.append(value)
    values.append(store)
  return values


async def get_intersection_values(groups: Groups) -> Dict[str, List[int]]:
  store = {}

  for position, neighbors in groups.intersections.positions.items():
    values = []
    for neighbor in neighbors:
      value = groups.grid[neighbor]
      values.append(value)
    store[position] = values

  return store


async def get_column_row_available_values(groups: Groups) -> Groups:
  group_names = ['rows', 'columns']
  for group_name in group_names:

    store = []
    group = getattr(groups, group_name)

    for row in group.values:
      available = []
      for i in range(1, groups.n + 1):
        count = row.count(i)
        if count == 2:
          return None
        if count != 0:
          continue
        available.append(i)
      store.append(available)
    group.available_values = store

  return groups


async def get_intersection_available_values(groups: Groups) -> Groups:
  if groups is None:
    return None

  store = {}

  for position, values in groups.intersections.values.items():
    if groups.grid[position] != 0:
      continue
    available = []
    for i in range(1, groups.n + 1):
      if i in values:
        continue
      available.append(i)
    if len(available) == 0:
      continue
    store[position] = available
  groups.intersections.available_values = store
  return groups


async def get_intersection_scores(groups: Groups) -> Groups:
  if groups is None:
    return None

  store = {}
  for position, available_values in groups.intersections.available_values.items():

    if groups.grid[position] != 0:
      continue

    score = 0
    for i in range(groups.n):
      if i not in available_values:
        score = score + 1
        continue
      if i in available_values:
        score = score + groups.values[i]
        continue

    # if score == 1:
    #   continue
    store[position] = round(score, 2)
  groups.intersections.scores = store
  return groups


async def get_row_column_scores(groups: Groups) -> Groups:
  if groups is None:
    return None

  group_names = ['rows', 'columns']
  for group_name in group_names:
    group = getattr(groups, group_name)
    store = []

    for i in range(groups.n):
      available_values = group.available_values[i]
      score = 0
      for j in range(1, groups.n + 1):
        if j not in available_values:
          score += 1
          continue
        if j in available_values:
          score += groups.values[j]
          continue
      score = round(score, 2)
      store.append(score)
    group.scores = store

  return groups


async def get_response(data: Data) -> dict:
  return {'solution': data.solution}


async def update_groups(groups: Groups) -> Groups:
  groups.values = await get_grid_values(grid=groups.grid, n=groups.n)
  # Get values
  groups.rows.values = await get_row_values(groups=groups)
  groups.columns.values = await get_column_values(groups=groups)
  groups.intersections.values = await get_intersection_values(
    groups=groups)
  # Get available values
  groups = await get_column_row_available_values(groups=groups)
  groups = await get_intersection_available_values(groups=groups)
  # Get scores
  groups = await get_intersection_scores(groups=groups)
  groups = await get_row_column_scores(groups=groups)
  
  # scores = list(groups.intersections.scores.values())
  # max_score = max(scores)
  # index = scores.index(max_score)
  # keys = list(groups.intersections.scores.keys())
  # position = keys[index]
  # print('position', position, groups.intersections.available_values[position])
  # raise RuntimeError()
  
  return groups


# TODO: Cleanup main. Only functions should be called in main.
# @error_handler.main(debug=False)
# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  grid: Dict | List | None = None,
) -> Data:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None

  grid = data.body.grid
  n = len(grid)
  if isinstance(grid, dict) is True:
    n = int(sqrt(len(data.body.grid)))
  if isinstance(grid, list) is True:
    grid = await grid_algorithms.main(grid=data.body.grid, convert_to='dict')
    print(grid)

  grid_values_total = list(grid.values())
  grid_values_total = sum(grid_values_total)
  data.tree = {grid_values_total: [grid]}
  data.groups = await get_groups(n=n)
  data.values_total = await get_values_total(n=n)

  conditions = []
  while True not in conditions:
    keys = list(data.tree.keys())
    max_values_total = max(keys)
    # if data.iterations.count % 2 == 0:
    #   max_values_total = min(keys)
    # print(data.iterations.count, max_values_total, list(data.tree.keys()))

    grids = data.tree[max_values_total]
    grids_n = len(grids)
    for i in reversed(range(grids_n)):
      groups = deepcopy(data.groups)
      groups.grid = deepcopy(grids[i])
      groups = await update_groups(groups=groups)

      # print(groups.intersections.scores)
      # print('\n')
      # for key, value in groups.intersections.available_values.items():
      #   print(key, value)
      # raise RuntimeError()

      if groups is None:
        del data.tree[max_values_total][i]
        if len(data.tree[max_values_total]) == 0:
          del data.tree[max_values_total]
        continue

      scores = list(groups.intersections.scores.values())

      if len(scores) == 0:
        values = list(data.tree[max_values_total][i].values())
        values_total = sum(values)

        # print(values_total, 'no scores')
        # for k in range(9):
        #   print(list(groups.grid.values())[k * 9: (k + 1) * 9])

        del data.tree[max_values_total][i]
        if len(data.tree[max_values_total]) == 0:
          del data.tree[max_values_total]
        continue

      max_scores = max(scores)
      index = scores.index(max_scores)
      positions = list(groups.intersections.scores.keys())
      position = positions[index]
      available_values = groups.intersections.available_values[position]

      for value in available_values:
        grid_copy = deepcopy(groups.grid)
        grid_copy[position] = value
        grid_values_total_b = list(grid_copy.values())
        grid_values_total_b = sum(grid_values_total_b)
        if grid_values_total_b not in data.tree:
          data.tree[grid_values_total_b] = []
        data.tree[grid_values_total_b].append(grid_copy)

      del data.tree[max_values_total][i]
      if len(data.tree[max_values_total]) == 0:
        del data.tree[max_values_total]

    conditions = [
      data.values_total in data.tree.keys(),
      data.iterations.count >= data.iterations.maximum,
      data.tree == {},
    ]
    data.iterations.count += 1

  # print(data.tree.keys())

  if data.values_total in data.tree:
    grid = data.tree[data.values_total][0]
    grid = await grid_algorithms.main(grid=grid, convert_to='list')
    data.solution = grid
  data.tree = None
  data.groups = None

  data = await get_response(data=data)
  return data

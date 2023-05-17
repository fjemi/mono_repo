# #!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import List, Dict
from copy import deepcopy

# from models import Data
# import get_group_positions
# import get_position_values
# import get_position_fill_percents
# import get_position_available_values
# import get_position_scores
import convert_grid

from shared.error_handler import app as error_handler
from shared.setup_data import app as setup_data


@dataclass
class Group:
  positions: Dict[str, int] | List[List[int]] | None = None
  values: Dict[str, List[int]] | List[List[int]] | None = None
  available_values: Dict[str, List[int]] | List[List[int]] | None = None
  scores: Dict[str, float] | None = None


@dataclass
class Groups:
  n: int = 0
  grid: Dict[str, int] | None = None
  rows: Group = field(default_factory=lambda: Group())
  columns: Group = field(default_factory=lambda: Group())
  intersections: Group = field(default_factory=lambda: Group())
  values: Dict[str, float] | None = None

class Store:
  pass


@dataclass
class Data:
  grid: List[List[int | str]] | None = None
  n: int = 0
  groups: Groups | None = None
  tree: List[List[Dict[str, int]]] | None = None
  values_total: int = 0
  completed: Dict | List | None = None
  iterations: int = 0
  max_iterations: int = 400


def get_values_total(n: int) -> int:
  store = 0
  _range = range(1, n + 1)
  for i in _range:
    store += i * n
  return store


def get_intersection_positions(n: int) -> Dict[str, List[str]]:
  store = {}
  _range = range(n)
  for i in _range:
    for j in _range:
      position = f'{i}.{j}'
      store[position] = []
      for k in _range:
        neighboor = f'{i}.{k}'
        store[position].append(neighboor)
        neighboor = f'{k}.{j}'
        if neighboor != position:
          store[position].append(neighboor)
  return store 


def get_row_positions(n: int) -> List[List[str]]:
  store = {}
  _range = range(n)
  for i in _range:
    store[i] = []
    for j in _range:
      position = f'{i}.{j}'
      store[i].append(position)
  return list(store.values())


def get_column_positions(n: int) -> List[List[str]]:
  _range = range(n)
  store = {}
  
  for i in _range:
    store[i] = []
    for j in _range:
      position = f'{j}.{i}'
      store[i].append(position)
  return store


def get_groups(
  n: int, 
  grid: Dict | None = None,
) -> Groups:
  store = Groups(n=n, grid=grid)
  store.intersections.positions = get_intersection_positions(n=n)
  store.rows.positions = get_row_positions(n=n)
  store.columns.positions = get_column_positions(n=n)
  return store
  

def get_grid_values(
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


def get_row_values(groups: Groups) -> List[List[int]]:
  values = []
  for i in range(groups.n):
    row = groups.rows.positions[i]
    store = []
    for position in row:
      value = groups.grid[position]
      store.append(value)
    values.append(store)
  return values

  
def get_column_values(groups: Groups) -> List[List[int]]:
  values = []
  for i in range(groups.n):
    row = groups.columns.positions[i]
    store = []
    for position in row:
      value = groups.grid[position]
      store.append(value)
    values.append(store)
  return values


def get_intersection_values(groups: Groups) -> Dict[str, List[int]]:
  store = {}
  
  for position, neighboors in groups.intersections.positions.items():
    values = []
    for neighboor in neighboors:
      value = groups.grid[neighboor]
      values.append(value)
    store[position] = values

  return store


def get_column_row_available_values(groups: Groups) -> Groups:
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


def get_intersection_available_values(groups: Groups) -> Groups:
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


def get_intersection_scores(groups: Groups) -> Groups:
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


def get_row_column_scores(groups: Groups) -> Groups:
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


def update_groups(groups: Groups) -> Groups:
  groups.values = get_grid_values(grid=groups.grid, n=groups.n)
  # Get values
  groups.rows.values = get_row_values(groups=groups)
  groups.columns.values = get_column_values(groups=groups)
  groups.intersections.values = get_intersection_values(
    groups=groups)
  # Get available values
  groups = get_column_row_available_values(groups=groups)
  groups = get_intersection_available_values(groups=groups)
  # Get scores
  groups = get_intersection_scores(groups=groups)
  groups = get_row_column_scores(groups=groups)
  return groups


# Add score to branches
# 


def process_data(data: Data) -> Data:
  store = Store()
  store.solution = None
  store.no_solution = []
  
  conditions = []
  while True not in conditions:
    conditions = [
      data.completed is not None,
      len(data.tree) == 0,
    ]

    tree_n = len(data.tree)
    for i in reversed(range(tree_n)):
      branches = data.tree[i]

      if None in branches:
        del data.tree[i]
        continue

      if {} in branches:
        data.completed = data.tree[i]
        break

      grid = branches[-1]
      values_total = sum(list(grid.values()))
      if values_total == data.values_total:
        data.completed = data.tree[i]

      groups = deepcopy(data.groups)
      groups.grid = grid
      groups = update_groups(groups=groups)

      if groups is None:
        store.no_solution.append(branches)
        del data.tree[i]
        continue

      groups_grid_total_value = sum(list(groups.grid.values()))
      if groups_grid_total_value == data.values_total:
        data.tree[i].append(groups.grid)
        data.completed = data.tree[i]
        break

      scores = list(groups.intersections.scores.values())

      if len(scores) == 0:
        del data.tree[i]
        continue
        # print(groups.grid)

      max_score = max(scores)
      index = scores.index(max_score)
      positions = list(groups.intersections.scores.keys())
      position = positions[index]
      available_values = groups.intersections.available_values[position]
      available_values_n = len(available_values)
      # print(available_values, len(data.tree), groups_grid_total_value,)
      
      if available_values_n == 1:
        grid_copy = deepcopy(grid)
        grid_copy[position] = available_values[0]
        data.tree[i].append(grid_copy)
        continue
        
      if available_values_n > 1:
        
        for value in available_values:
          branches_copy = deepcopy(data.tree[i])
          grid_copy = deepcopy(grid)
          grid_copy[position] = value
          branches_copy.append(grid_copy)
          data.tree.append(branches_copy)
        del data.tree[i]
        continue
  
    data.iterations += 1
    if data.iterations > data.max_iterations:
      break

  return data
  


def main(data: Data | dict | str) -> Data:
  data = setup_data.main(data=data, data_class=Data)
  data.n = len(data.grid)
  grid_dict = convert_grid.main(grid=data.grid)
  data.tree = [[grid_dict]]
  data.groups = get_groups(n=data.n)
  data.values_total = get_values_total(n=data.n)
  data = process_data(data=data)
  

  data.tree = None
  data.groups = None
  if isinstance(data.completed, list):
    grid_dict = data.completed[-2]
    grid_list = convert_grid.main(grid=grid_dict)
    data.completed = grid_list
  # print(data)
  return data


def example() -> None:
  from shared.execute_example_data import app as execute_example_data


  examples = '''
    examples:
    - grid:
      - [0, 0]
      - [0, 1]
    - grid:
      - [0,0,0]
      - [1,0,3]
      - [0,0,0]
    - grid:
      - [9,6,2,0,3,5,8,0,9]
      - [0,0,5,0,0,6,0,0,0]
      - [4,0,0,0,8,0,2,0,6]
      - [0,0,0,7,4,9,1,3,0]
      - [0,9,0,3,0,0,7,6,0]
      - [0,0,3,0,0,0,5,0,8]
      - [0,2,0,8,6,7,9,1,5]
      - [0,0,6,0,0,3,0,0,0]
      - [1,7,0,5,0,0,0,8,0]
    - grid:
      - [9,6,2,0,3,5,8,0,0]
      - [0,0,5,0,0,6,0,0,9]
      - [4,0,0,0,8,0,2,0,6]
      - [0,0,0,7,4,9,1,3,0]
      - [0,9,0,3,0,0,7,6,0]
      - [0,0,3,0,0,0,5,0,8]
      - [0,2,0,8,6,7,9,1,5]
      - [0,0,6,0,0,3,0,0,0]
      - [1,7,0,5,0,0,0,8,0]
    # - grid:
    #   - [0,0,1,0,0,6,0,0,3]
    #   - [0,0,6,3,0,9,8,0,0]
    #   - [2,5,0,6,0,3,0,0,0]
    #   - [0,0,0,0,0,0,0,0,0]
    #   - [0,8,7,0,0,0,0,4,0]
    #   - [0,0,0,0,9,0,7,0,0]
    #   - [0,0,0,0,0,4,0,1,0]
    #   - [0,0,0,0,0,2,0,0,5]
    - grid:
      - [0,0,0,0,2,0,4,0,0]
      - [9,0,6,0,8,0,0,0,0]
      - [0,0,0,0,0,3,0,0,6]
      - [0,0,0,0,0,0,7,5,4]
      - [3,8,0,0,0,0,0,2,0]
      - [1,0,0,0,0,0,0,3,0]
      - [0,5,0,4,0,0,0,0,2]
      - [0,7,0,0,0,0,0,0,0]
      - [0,0,3,5,0,7,0,0,0]
  '''
  execute_example_data.main(
    examples=examples,
    main_function=main,
  )


if __name__ == '__main__':
  example()

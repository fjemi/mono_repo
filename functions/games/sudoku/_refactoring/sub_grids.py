import dataclasses as dc
from typing import List, Dict
from math import floor, sqrt


class Store:
  ...


@dc.dataclass
class SubGrids:
  n: int = 0
  values_total: int = 0
  grids: Dict[str, List[str]] | None = None
  positions: Dict[str, List[str]] | None = None
  values: Dict[str, List[int]] | None = None
  scores: Dict[str, float] | None = None


def is_square_sudoku(n: int) -> bool:
  m = sqrt(n)
  # Check if square root is a whole number
  if m != int(m):
    return False
  return True


def get_sub_grid_label(
  k: int,
  position: str = None,
  i: int = None,
  j: int = None,
) -> str:
  if position:
    i, j = position.split('.')
  i = int(i)
  j = int(j)
  row = floor(i / k)
  column = floor(j / k)
  label = f'{row}.{column}'
  return label


def initialize_sub_grids(n: int) -> SubGrids:
  k = int(sqrt(n))
  store = {}
  values_total = 0
  for i in range(n):
    values_total += i + 1
    for j in range(n):
      label = get_sub_grid_label(k=k, i=i, j=j)
      store[label] = []
  sub_grids = SubGrids(
    grids=store,
    n=n,
    values_total=values_total,
  )
  return sub_grids


def get_positions_for_sub_grids(
  sub_grids: SubGrids,
) -> SubGrids:
  k = int(sqrt(sub_grids.n))
  for i in range(0, sub_grids.n):
    for j in range(0, sub_grids.n):
      grid_position = f'{i}.{j}'
      label = get_sub_grid_label(i=i, j=j, k=k)
      sub_grids.grids[label].append(grid_position)
  return sub_grids


def get_sub_grids_by_positions(sub_grids: SubGrids) -> SubGrids:
  store = {}
  for label, positions in sub_grids.grids.items():
    for position in positions:
      store[position] = label
  sub_grids.positions = store
  return sub_grids


def get_values_for_sub_grids_list(
  grid: List[List[int]], 
  sub_grids: SubGrids,
) -> SubGrids:
  store = {}
  for grid_position, positions in sub_grids.grids.items():
    values = []
    for position in positions:
      i, j = position.split('.')
      i = int(i)
      j = int(j)
      value = grid[i][j]
      values.append(value)
    store[grid_position] = values
  sub_grids.values = store
  return sub_grids


def get_values_for_sub_grids_dict(
  grid: Dict, 
  sub_grids: SubGrids,
) -> SubGrids:
  store = {}
  
  
  return sub_grids
  

def get_values_for_sub_grids(
  grid: Dict | List, 
  sub_grids: SubGrids,
  _locals: Dict = locals(),
) -> SubGrids:
  grid_type = type(grid).__name__
  function_name = f'get_values_for_sub_grids_{grid_type}'
  function = _locals[function_name]
  result = function(grid=grid, sub_grids=sub_grids)
  return result
  

n = 9
grid = [
  [0, 0, 0, 0, 0, 0, 0, 1, 0],
  [4, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 2, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 5, 0, 4, 0, 7],
  [0, 0, 8, 0, 0, 0, 3, 0, 0],
  [0, 0, 1, 0, 9, 0, 0, 0, 0],
  [3, 0, 0, 4, 0, 0, 2, 0, 0],
  [0, 5, 0, 1, 0, 0, 0, 0, 0],
  [0, 0, 0, 8, 0, 6, 1, 0, 0],
]
grid = [
  [0, 0, 0, 0, 0, 0, 0, 1, 0],
  [4, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 2, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 5, 0, 4, 0, 7],
  [0, 0, 8, 0, 0, 0, 3, 0, 0],
  [0, 0, 1, 0, 9, 0, 0, 0, 0],
  [3, 1, 9, 4, 7, 5, 2, 6, 8],
  [8, 5, 6, 1, 2, 9, 7, 0, 0],
  [0, 0, 0, 8, 3, 6, 1, 0, 0],
]

# grid = [
#   [6, 3, 5, 8, 2, 1, 4, 9, 7],
#   [9, 1, 6, 2, 8, 4, 3, 7, 5],
#   [5, 4, 2, 1, 7, 3, 9, 8, 6],
#   [8, 6, 9, 3, 1, 2, 7, 5, 4],
#   [3, 8, 7, 9, 4, 5, 6, 2, 1],
#   [1, 9, 4, 7, 5, 6, 2, 3, 8],
#   [7, 5, 8, 4, 3, 9, 1, 6, 2],
#   [2, 7, 1, 6, 9, 8, 5, 4, 3],
#   [4, 2, 3, 5, 6, 7, 8, 1, 9],
# ]

# n = 2
# grid = [
#   [0, 0],
#   [0, 1],
# ]

# n = 4
# grid = [
#   [0, 0, 0, 0],
#   [0, 1, 0, 0],
#   [0, 0, 2, 0],
#   [0, 0, 0, 3],
# ]

sub_grids = initialize_sub_grids(n=n)
sub_grids = get_positions_for_sub_grids(sub_grids=sub_grids)
sub_grids = get_sub_grids_by_positions(sub_grids=sub_grids)
sub_grids = get_values_for_sub_grids(
  grid=grid,
  sub_grids=sub_grids,
)


print('\n', sub_grids)

intersections = Store()
intersections.positions= {}
for i in range(n):
  for j in range(n):
    if grid[i][j] != 0:
      continue
    position = f'{i}.{j}'
    store = []
    for k in range(n):
      neighbor = f'{i}.{k}'
      if neighbor != position:
        store.append(neighbor)
      neighbor = f'{k}.{j}'
      if neighbor != position:
        store.append(neighbor)
      store.sort()
    intersections.positions[position] = store

intersections.values = {}
for position, neighbors in intersections.positions.items():
  values = []
  for neighbor in neighbors:
    i, j = neighbor.split('.')
    i = int(i)
    j = int(j)
    value = grid[i][j]
    values.append(value)
  intersections.values[position] = values

print(intersections.positions, intersections.values, sep='\n\n')

available = {}
for position in intersections.values:
  label = sub_grids.positions[position]
  position_data = {
    'position': position, 
    'intersection': intersections.values[position],
    'sub_grid': sub_grids.values[label],
  }
  print(position_data, '\n')
  store = []
  for i in range(n):
    value = i + 1
    # if value not in position_data['intersection']:
    if value not in position_data['intersection'] + position_data['sub_grid']:
      store.append(value)
  store_n = len(store)
  if store_n not in available:
    available[store_n] = {}
  available[store_n][position] = store

keys = list(available.keys())
keys.sort()

for key in keys:
  print(key, available[key], '\n\n')


grid = {
  '0.0': 0,
  '0.1': 1,
  '1.0': 0,
  '1.1': 2,
}
store = {}
for key, value in grid.items():
  if value not in store:
    from dotmap import DotMap
    store[value] = DotMap()
    store[value].rows = []
    store[value].columns = []
  row, column = key.split('.')
  row = int(row)
  column = int(column)
  store[value].rows.append(row)
  store[value].columns.append(column)

for key, value in store.items():
  print(key, value)
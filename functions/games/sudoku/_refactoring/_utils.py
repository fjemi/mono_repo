

import dataclasses as dc
from typing import Dict, List
from math import sqrt

from models import Groups


@dc.dataclass
class Data:
  grid: List[List[int]] | Dict[str, int] | None = None
  
  
class Store:
  pass


def convert_grid_to_branch_from_dictionary(
  grid: Dict[str, str],
) -> str:
  branch = ''
  for position, value in grid:
    leaf = '|{position},{value}'
    branch = branch + leaf
  branch = branch[1:]
  return branch


def convert_grid_to_dictionary_from_branch(
  branch: str,
) -> Dict[str, str]:
  store = {}
  leaves = branch.split('|')
  for leaf in leaves:
    position, value = leaf.split(',')
  store[position] = value
  return store



def get_positions_by_values(
  grid: Dict[str, str],
) -> Dict[str, List[str]]:
  n = len(grid)
  store = initialize_values_store(n=n)
  for position, value in grid.items():
    if value not in store:
      continue
    store[value].append(position)
  return store


def convert_grid_to_dictionary(
  grid: List[List[int | str]],
  data: Data | dict | str | None = None,
) -> Dict[str, str]:
  
  store = {}
  grid_range = range(len(grid))
  for i in grid_range:
    for j in grid_range:
      position = f'{i}.{j}'
      value = grid[i][j]
      store[position] = value
  return store


def convert_grid_to_list(
  grid: Dict[str, int],
  n: int,
) -> List[List[int]]:
  if grid in [None, []]:
    return []
    
  store = [[] for i in range(n)]
  for position in grid:
    i = position.split('.')[0]
    i = int(i)
    store[i].append(grid[position])
  return store


def case_list_grid_to_dict(
  grid: List[List[int]],
) -> Dict[str, int]:
  store = {}
  grid_range = range(len(grid))
  for i in grid_range:
    for j in grid_range:
      position = f'{i}.{j}'
      value = grid[i][j]
      store[position] = value
  return store
  
  
def case_dict_grid_to_list(
  grid: Dict[str, int],
) -> List[List[int]]:
  store = []
  
  for position in grid:
    i, j = position.split('.')
    i = int(i)
    j = int(j)
    if len(store) < i + 1:
      store.append([])
    value = grid[position]
    store[i].append(value)
  return store

  
MAIN = {
  'list': case_list_grid_to_dict,
  'dict': case_dict_grid_to_list,
}


def main(
  grid: Dict[str, int] | List[List[int]],
) -> Dict[str, int] | List[List[int]]:
  grid_type = type(grid).__name__
  function = MAIN[grid_type]
  result = function(grid=grid)
  return result


def example() -> None:
  import yaml
  
  
  examples = '''
    - grid:
      - [0, 0]
      - [1, 1]
    - grid:
        '0.0': 0
        '0.1': 0
        '1.0': 1
        '1.1': 1
  '''
  examples = yaml.safe_load(examples)
  for example in examples:
    print(example, main(**example), sep='\n')
  
  
if __name__ == '__main__':
  example()
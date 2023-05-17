#!/usr/bin/env python3

# from dataclasses import dataclass, field
from typing import List, Dict
from copy import deepcopy

from models import Data
import get_group_positions
import get_position_values
import get_position_fill_percents
import get_position_available_values
import get_position_scores
import _utils

from shared.error_handler import app as error_handler
from shared.setup_data import app as setup_data



def pre_processing(data: Data) -> Data:
  data.n = len(data.grid)
  value_totals = [i * data.n for i in range(data.n + 1)]
  data.completed_values_total = sum(value_totals)
  data.positions = get_group_positions.main(n=data.n)
  
  grid_dict = _shared.main(grid=data.grid)
  data.tree = [[grid_dict]]
  return data


class Store:
  pass


def case_available_n_is_zero(
  grids: List[Dict[str, int]],
  position: str,
  available: int,
) -> List:
  return grids


def case_available_n_is_one(
  grids: List[Dict[str, int]],
  position: str,
  available: int,
) -> List[Dict[str, int]]: 
  store = []
  for grid in grids:
    grid = deepcopy(grids[0])
    grid[position] = available[0]
    store.append(grid)
  return store
  
  
def case_available_n_is_greater_than_one(
  grids: List[Dict[str, int]],
  position: str,
  available: int,
) -> List[Dict[str, int]]: 
  store = []
  for value in available:
    for grid in grids:
      grid = deepcopy(grid)
      grid[position] = value
      store.append(grid)
  return store


SET_NEXT_GRIDS = {
  '1.0': case_available_n_is_zero,
  '0.1': case_available_n_is_one,
  '0.0': case_available_n_is_greater_than_one,
}


def set_next_grids(
  scores: Dict[float, List[dict]],
  grid: Dict[str, str],
) -> List[Dict[str, int]]:
  next_grids = [grid]

  for score in scores:
    positions_values = scores[score]
    _range = range(len(positions_values))

    for i in _range:
      available = positions_values[i].available
      available_n = len(available)
      cases = [
        int(available_n == 0),
        int(available_n == 1),
      ]
      cases = f'{cases[0]}.{cases[1]}'
      function = SET_NEXT_GRIDS[cases]
      next_grids = function(
        available=available,
        position=positions_values[i].position,
        grids=next_grids,
      )
      next_grids_n = len(next_grids)
      
      for grid in next_grids:
        values = list(grid.values())
        print(sum(values))
      break
      if next_grids_n > 1:
        return next_grids
    break
  print(next_grids)
  return next_grids


@error_handler.main(debug=True)
def main(data: Data | dict | str) -> Data:
  data = setup_data.main(data=data, data_class=Data)
  data = pre_processing(data=data)

  while data.completed is None:
    grids = data.tree[-1]
    new_grids_store = []

    for grid in grids:
      values = get_position_values.main(
        positions=data.positions,
        grid=grid,
      )

      if values is None:
        continue

      percents = get_position_fill_percents.main(
        values=values,
        grid=grid,
      )
      available = get_position_available_values.main(
        values=values,
        grid=grid,
      )
      scores = get_position_scores.main(
        available=available,
        percents=percents,
        grid=grid,
      )
      new_grids = set_next_grids(
        scores=scores,
        grid=grid,
      )
      new_grids_store.extend(new_grids)
    data.tree.append(new_grids_store)

    sum_store = []
    for grid in data.tree[-1]:
      sum_grid = sum(list(grid.values()))
      sum_store.append(sum_grid)

    if data.completed_values_total in sum_store:
      _index = sum_store.index(data.completed_values_total)
      data.completed = data.tree[-1][_index]
      break

    if len(data.tree[-1]) == 0:
      data.completed = []
    print(data.tree)
    break

  # Post processing
  data.completed = _shared.convert_grid_to_list(
    grid=data.completed,
    n=data.n,
  )
  data.tree = None
  data.positions = None
  return data


def example() -> None:
  from shared.execute_example_data import app as execute_example_data


  examples = '''
    examples:
    # - grid:
    #   - [0, 0]
    #   - [0, 1]
    # - grid:
    #   - [0,0,0]
    #   - [1,0,3]
    #   - [0,0,0]
    # - grid:
    #   - [9,6,2,0,3,5,8,0,9]
    #   - [0,0,5,0,0,6,0,0,0]
    #   - [4,0,0,0,8,0,2,0,6]
    #   - [0,0,0,7,4,9,1,3,0]
    #   - [0,9,0,3,0,0,7,6,0]
    #   - [0,0,3,0,0,0,5,0,8]
    #   - [0,2,0,8,6,7,9,1,5]
    #   - [0,0,6,0,0,3,0,0,0]
    #   - [1,7,0,5,0,0,0,8,0]
    # - grid:
    #   - [9,6,2,0,3,5,8,0,0]
    #   - [0,0,5,0,0,6,0,0,9]
    #   - [4,0,0,0,8,0,2,0,6]
    #   - [0,0,0,7,4,9,1,3,0]
    #   - [0,9,0,3,0,0,7,6,0]
    #   - [0,0,3,0,0,0,5,0,8]
    #   - [0,2,0,8,6,7,9,1,5]
    #   - [0,0,6,0,0,3,0,0,0]
    #   - [1,7,0,5,0,0,0,8,0]
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

'''
[Position()]
'''
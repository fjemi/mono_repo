#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class Data:
  items: List[Any] | None = None
  combinations: List[List] | None = None
  positions: List[List] | None = None
  return_positions: bool = False
  values: List[List[Any]] | None = None


def set_combinations_and_positions(data: Data) -> Data:
  positions = []

  for i in range(len(data.items)):
    data.positions.append([i])
    positions.append(i)

  data.positions.append(positions)
  data.combinations.append(positions)
  return data


def get_combinations(data: Data) -> Data:
  # TODO:
  # positions = {}
  # values = {}

  n = len(data.items)
  if n >= 3:
    n = n - 2
  for k in range(n):
    store = []
    for item_i in data.combinations[0]:
      for item_j in data.combinations[-1]:
        # Format item as list if needed
        if not isinstance(item_j, list):
          item_j = [item_j]
        # Handle duplicate positions within a combination
        if item_i in item_j or item_i == item_j:
          continue
        # Create the combination
        combination = item_j + [item_i]
        combination.sort()
        # Ignore combinations that have already been added -> (1, 2) and (2, 1)
        if combination in store:
          continue
        store.append(combination)
    data.positions = data.positions + store
    data.combinations.append(store)
  return data


def get_combination_values(data: Data) -> List:
  '''Returns values associated with combinations of positions'''
  store = []
  # Get the value associated with each position in a combination
  for position in data.positions:
    combination = []
    for i in position:
      value = data.items[i]
      combination.append(value)
    store.append(combination)
  data.values = store
  return store


def main(data: Data | dict | str) -> Data:
  data = set_combinations_and_positions(data=data)
  data = get_combinations(data=data)

  if data.return_positions is True:
    return data.positions

  data.values = get_combination_values(data=data)
  return data


def example() -> None:
  data = '''
    items: [a, b, c]
  '''
  data = main(data=data)
  print(data)


if __name__ == '__main__':
  example()
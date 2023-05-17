#!/usr/bin/env python3

from typing import Dict, List
from dataclasses import dataclass

from models import Base


@dataclass
class Positions(Base):
  pass


def initialize_values(n: int) -> Dict[str, List[str]]:
  _range = range(n + 1)
  values = [i for i in _range]
  store = {}
  for value in values:
    store[value] = 0
  return store


def initialize_intersections(n: int) -> Dict[str, str]:
  _range = range(n)
  store = {}
  for i in _range:
    for j in _range:
      position = f'{i}.{j}'
      intersection = {}
      for k in _range:
      #   row_position = f'{i}.{k}'
      #   if row_position != position:
      #     intersection[row_position] = None
      #   column_position = f'{k}.{j}'
      #   if column_position != position:
      #     intersection[column_position] = None
        row_position = f'{i}.{k}'
        intersection[row_position] = None
        column_position = f'{k}.{j}'
        intersection[column_position] = None
      intersection = list(intersection.keys())
      store[position] = intersection
  return store


def initialize_rows(n: int) -> List[List[str]]:
  _range = range(n)
  store = [[] for i in _range]
  for i in _range:
    for j in _range:
      position = f'{i}.{j}'
      store[j].append(position)
  return store


def initialize_columns(n: int) -> List[List[str]]:
  _range = range(n)
  store = [[] for i in _range]
  for i in _range:
    for j in _range:
      position = f'{i}.{j}'
      store[i].append(position)
  return store


def main(n: int = None) -> Positions:
  positions = Positions(
    n=n,
    values=initialize_values(n=n),
    rows=initialize_rows(n=n),
    columns=initialize_columns(n=n),
    intersections=initialize_intersections(n=n),
  )
  return positions


def example() -> None:
  positions = main(n=2)
  print(positions)
  

if __name__ == '__main__':
  example()
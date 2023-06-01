

import dataclasses as dc
from typing import List, Dict
from copy import deepcopy

from models import Base


@dc.dataclass
class Available(Base):
  pass


# def get_values(values: 'Values') -> Dict[int, float]:
#   store = {}
#   for value, count in values.values.items():
#     percent = count / values.n
#     percent = round(percent, 2)
#     store[value] = percent
#   return store

  

def get_intersections(
  available: Available,
  values: 'Values',
  grid: Dict[str, int],
) -> Available:
  store = {}
  for position, intersection in values.intersections.items():
    if grid[position] != 0:
      continue
    
    available_values = []
    for value in values.values:
      if value in intersection:
        continue
      available_values.append(value)
    store[position] = available_values
  available.intersections = store
  return available


def get_rows_and_columns(
  values: 'Values',
  available: Available,
) -> Available:
  _range = range(values.n)
  available.rows = []
  available.columns = []
  for i in _range:
    row = []
    column = []
    for value in values.values:
      if value not in values.rows[i]:
        row.append(value)
      if value not in values.columns[i]:
        column.append(value)
    available.rows.append(row)
    available.columns.append(column)
  return available


def main(
  values: 'Values',
  grid: Dict[str, int],
) -> Available:
  available = Available()
  available = get_intersections(
    available=available,
    values=values,
    grid=grid,
  )
  available = get_rows_and_columns(values=values, available=available)
  return available
  
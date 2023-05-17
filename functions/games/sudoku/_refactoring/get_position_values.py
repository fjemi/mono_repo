#!/usr/bin/env python3

from typing import Dict, List
from dataclasses import dataclass, fields
from copy import deepcopy

from models import Base


@dataclass
class Values(Base):
  pass


def initialize_values(
  positions: 'Positions', 
  grid: Dict[str, int],
) -> Values:
  values = Values()
  for _field in fields(positions):
    value = getattr(positions, _field.name)
    value = deepcopy(value)
    setattr(values, _field.name, value)
  if grid is not None:
    values.grid = grid
  return values


def set_rows_or_columns(
  values: Values,
  grid: Dict[str, int],
  rows: bool = True,
) -> Values:
  group_name = 'columns'
  if rows is True:
    group_name = 'rows'
  group = getattr(values, group_name)
  
  _range = range(values.n)
  for i in _range:
    for j in _range:
      position = group[i][j]
      value = grid[position]
      group[i][j] = value
  setattr(values, group_name, group)
  return values


def set_intersections(
  values: Values,
  grid: Dict[str, int],
) -> Values:
  for position, neighboors in values.intersections.items():
    if grid[position] != 0:
      continue

    store = []
    for neighboor in neighboors:
      value = grid[neighboor]
      store.append(value)
    values.intersections[position] = store
  return values


def set_value_counts(
  values: Values,
  grid: Dict[str, int],
) -> Values:
  grid_values = list(grid.values())
  for value in values.values:
    count = grid_values.count(value)
    values.values[value] = count
  return values


def validate_row_and_column_values(
  values: Values,
) -> Values | None:
  _range = range(values.n)
  for i in _range:
    for value in values.values:
      if value == 0:
        continue
      
      row = values.rows[i]
      column = values.columns[i]
      counts = [
        row.count(value),
        column.count(value),
      ]
      if 2 in counts:
        return None
  return values


def main(
  positions: 'Positions',
  grid: Dict[str, int] = None,
  values: Values = None
) -> Values | None:
  if values is None:
    values = initialize_values(positions=positions, grid=grid)
  
  values = set_rows_or_columns(values, rows=True, grid=grid)
  values = set_rows_or_columns(values, rows=False, grid=grid)
  values = set_intersections(values=values, grid=grid)
  values = set_value_counts(values=values, grid=grid)
  values = validate_row_and_column_values(values=values)
  return values


def example() -> None:
  import initialize_positions
  
  grid = {'0.0': 1, '0.1': 2, '1.0': 0, '1.1': 0}
  n = 2
  positions = initialize_positions.main(n=n)
  values = main(positions=positions, grid=grid)
  print(values, positions, sep='\n\n')


if __name__ == '__main__':
  example()

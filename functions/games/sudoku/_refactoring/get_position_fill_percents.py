

from dataclasses import dataclass
from typing import List, Dict

from models import Base


@dataclass
class Percents(Base):
  pass


def get_values(values: 'Values') -> Dict[int, float]:
  store = {}
  for value, count in values.values.items():
    percent = count / values.n
    percent = round(percent, 2)
    store[value] = percent
  return store


def get_fill_percent(group: List[int]) -> float:
  count = group.count(0)
  percent = 1 - count / len(group)
  percent = round(percent, 2)
  return percent
  

def get_intersections(
  values: 'Values', 
  percents: Percents,
  grid: Dict[str, int],
) -> Percents:
  store = {}
  for position, group in values.intersections.items():
    if grid[position] != 0:
      continue
    percent = get_fill_percent(group=group)
    store[position] = percent
  percents.intersections = store
  return percents


def get_rows_and_columns(
  values: 'Values',
  percents: Percents,
) -> Percents:
  _range = range(values.n)
  percents.rows = []
  percents.columns = []
  for i in _range:
    group = values.rows[i]
    percent = get_fill_percent(group=group)
    percents.rows.append(percent)
    group = values.columns[i]
    percent = get_fill_percent(group=group)
    percents.columns.append(percent)
  return percents


def main(
  values: 'Values',
  grid: Dict[str, int],
) -> Percents:
  percents = Percents(
    values=get_values(values=values),
  )
  percents = get_intersections(
    values=values, 
    percents=percents, 
    grid=grid,
  )
  percents = get_rows_and_columns(values=values, percents=percents)
  return percents
  
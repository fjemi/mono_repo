#!/usr/bin/env python3

from typing import Dict, List
import dataclasses as dc
from copy import deepcopy

from models import Base, Store


@dc.dataclass
class Scores(Base):
  pass


# def set_rows_or_columns(
#   values: Values, 
#   rows: bool = True,
# ) -> Values:
#   group_name = 'columns'
#   if rows is True:
#     group_name = 'rows'
#   group = getattr(values, group_name)
  
#   _range = range(values.n)
#   for i in _range:
#     for j in _range:
#       position = group[i][j]
#       value = values.grid[position]
#       group[i][j] = value
#   setattr(values, group_name, group)
#   return values


def set_intersections(
  available: 'Available',
  percents: 'Percents',
  scores: Scores,
  grid: Dict[str, int],
) -> Scores:
  scores.intersections = {}
  for position, available_values in available.intersections.items():
    if grid[position] != 0:
      continue

    store = []
    for value in available_values:
      percent = percents.values[value]
      store.append(percent)
      
    n = Store()
    n.store = len(store)  
    n.values = len(percents.values) - 1
    score = sum(store) + n.values - n.store
    score = round(score, 2)
    scores.intersections[position] = score
  return scores


def get_positions_by_score(
  available: 'Available',
  scores: Scores,
) -> Scores:
  positions_by_score = {}
  for position, score in scores.intersections.items():
    if score not in positions_by_score:
      positions_by_score[score] = []
    store = Store()
    store.position = position
    store.available = available.intersections[position]
    positions_by_score[score].append(store)
  return positions_by_score


def sort_positions_by_score(
  positions_by_score: Dict[float, List[dict]],
) -> Dict[float, List[dict]]:
  store = {}
  keys = list(positions_by_score.keys())
  keys.sort(reverse=True)
  for key in keys:
    store[key] = positions_by_score[key]
  return store


def main(
  available: 'Available',
  percents: 'Percents',
  grid: Dict[str, int],
) -> Dict[float, List[dict]]:
  scores = Scores()
  scores = set_intersections(
    scores=scores,
    available=available,
    percents=percents,
    grid=grid,
  )
  positions_by_score = get_positions_by_score(
    available=available,
    scores=scores,
  )
  positions_by_score = sort_positions_by_score(
    positions_by_score=positions_by_score)
  return positions_by_score


def example() -> None:
  pass


if __name__ == '__main__':
  example()

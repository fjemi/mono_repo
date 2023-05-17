#!/usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import List, Dict
from copy import deepcopy
import yaml

from api import models


@dataclass
class Body(models.Body):
  card_points: List[int] | None = None
  k: int = 0


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  k_cards: List[int] | Dict[int, List[List[int]]] | None = None


@dataclass
class Branches:
  previous: List[Dict] | None = None
  current: List[Dict] | None = None


async def case_k_greater_than_equal_to_n(data: Data) -> Data:
  value = sum(data.body.card_points)
  points_as_strings = [str(x) for x in data.body.card_points]
  key = '.'.join(points_as_strings)
  data.k_cards = {value: [key]}
  return data


async def get_tree_roots(card_points) -> List[dict]:
  left = str(card_points[0])
  right = str(card_points[-1])
  roots = [
    {left: card_points[1:]},
    {right: card_points[:-1]},
  ]
  tree = [roots]
  return tree


async def get_tree_branches(
  tree: List[List[Dict[str, List[int]]]],
  k: int,
) -> List[List[Dict[str, List[int]]]]:
  branches = Branches()

  for i in range(k - 1):
    branches.previous = tree[i]
    branches.current = []

    for branch in branches.previous:
      key = list(branch.keys())[0]
      values = branch[key]

      left_key = f'{key}.{values[0]}'
      left_values = values[1:]
      right_key = f'{key}.{values[-1]}'
      right_values = values[:-1]

      branches.current.extend([
        {left_key: left_values},
        {right_key: right_values},
      ])
    tree.append(branches.current)
  return tree


async def aggregate_last_branches_in_tree(
  tree: List[List[Dict[str, List[int]]]],
) -> Dict[int, List[str]]:
  store = {}
  for branch in tree[-1]:
    branch = list(branch.keys())[0]
    leaves = branch.split('.')
    total = sum([int(x) for x in leaves])
    if total not in store:
      store[total] = []
    store[total].append(branch)
  return store


async def case_k_less_than_n(data: Data) -> Data:
  tree = await get_tree_roots(card_points=data.body.card_points)
  tree = await get_tree_branches(tree=tree, k=data.body.k)
  tree = await aggregate_last_branches_in_tree(tree=tree)
  max_total = max(tree.keys())
  data.k_cards = {max_total: tree[max_total]}
  return data


N_K_SWITCHER = {
  'greater_than_equal': case_k_greater_than_equal_to_n,
  'less_than': case_k_less_than_n,
}


async def get_max_points(data: Data) -> Data:
  n = len(data.body.card_points)
  cases = [
    int(n <= data.body.k) * 'greater_than_equal',
    int(n > data.body.k) * 'less_than',
  ]
  cases = ''.join(cases)
  switcher = N_K_SWITCHER[cases]
  data = await switcher(data=data)
  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      max_points:
        n: {list(data.k_cards.keys())}
        cards: {list(data.k_cards.values())[0]}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data = await get_max_points(data=data)
  data = await get_response(data=data)
  return data

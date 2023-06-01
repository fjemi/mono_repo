#!usr/bin/env python3

from typing import List, Dict
import dataclasses as dc
from copy import deepcopy
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  budget: float | int = 0
  prices: List[float | int] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  prices: List[List[int]] = dc.field(default_factory=lambda: [])
  price_combinations: List[str] | None = None
  max_toys_under_budget: List[float | int] = dc.field(
    default_factory=lambda: [])


async def filter_prices(data: Data) -> List[int]:
  prices = deepcopy(data.body.prices)
  prices.sort()

  n = len(prices)
  for i in reversed(range(n)):
    price = prices[i]
    if price <= data.body.budget:
      break
    del prices[i]
  return prices


async def get_price_combinations(
  prices: List[int],
) -> List[List[str]]:
  n = len(prices)
  roots = [[x] for x in prices]
  tree = [roots]

  for i in range(n - 1):
    _ = i

    next_branches = []
    previous_branches = tree[-1]
    for branch in previous_branches:
      for price in prices:
        if price in branch:
          continue
        next_branch = deepcopy(branch) + [price]
        if next_branch in next_branches:
          continue
        next_branches.append(next_branch)
      tree.append(next_branches)

  return tree


async def get_single_list_of_combinations(
  price_combinations: List[List[List[int]]],
) -> List[List[int]]:
  store = []
  for combinations in price_combinations:
    for combination in combinations:
      combination.sort()
      if combination in store:
        continue
      store.append(combination)
  return store


async def total_price_combinations(
  price_combinations: List[List[int]],
) -> Dict[int, List[str]]:
  store = {}
  for combination in reversed(price_combinations):
    total = sum(combination)
    if total not in store:
      store[total] = []
    combination = [str(x) for x in combination]
    combination = '.'.join(combination)
    store[total].append(combination)
  return store


async def get_max_total_price(
  price_combinations: Dict[str, List[str]],
) -> Dict[str, List[str]]:
  store = {}
  if not price_combinations:
    return store
  max_price_total = max(price_combinations)
  store[max_price_total] = price_combinations[max_price_total]
  return store


async def aggregate_price_combinations(data: Data) -> Data:
  store = await get_single_list_of_combinations(
    price_combinations=data.price_combinations)
  store = await total_price_combinations(
    price_combinations=store)
  data.price_combinations = await get_max_total_price(
    price_combinations=store)
  return data


async def get_response(data: Data) -> dict:
  data = {
    'max_price': list(data.price_combinations.keys())[0],
    'prices': list(data.price_combinations.values())[0],
  }
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  budget: float | int | None = None,
  prices: List[float | int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.prices = await filter_prices(data=data)
  data.price_combinations = await get_price_combinations(prices=data.prices)
  data = await aggregate_price_combinations(data=data)
  data = await get_response(data=data)
  return data


async def example() -> None:
  result = await main(
    prices=[1, 12, 5, 111, 200, 1000, 10],
    budget=50,
  )
  print(result)


if __name__ == '__main__':
  import asyncio


  asyncio.run(example())

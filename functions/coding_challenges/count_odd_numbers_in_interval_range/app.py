#!usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from math import floor, ceil
from copy import deepcopy
import yaml

from api import models


@dataclass
class Body(models.Body):
  interval: List[int] | None = None


@dataclass
class RequestData(models.Data):
  body: Body = field(default_factory=lambda: Body())


@dataclass
class Request(models.Request):
  data: RequestData = field(default_factory=lambda: Data())


@dataclass
class Data:
  body: Body | None = None
  intervals: List[List[int]] | None = None
  odds: int = 0


async def case_both_numbers_are_zero(data: Data) -> Data:
  data.intervals = [deepcopy(data.body.interval)]
  return data


async def case_one_number_is_zero(data: Data) -> Data:
  data.intervals = [deepcopy(data.body.interval)]
  return data


async def case_numbers_have_same_parity(a: int, b: int) -> List[List[int]]:
  store = [[a, b]]
  return store


async def case_numbers_have_different_parity(a: int, b: int) -> List[List[int]]:
  store = [
    [a, 0],
    [b, 0],
  ]
  return store


async def case_numbers_are_the_same_and_nonzero(
  a: int, 
  b: int,
) -> List[List[int]]:
  if a % 2 == 0:
    store = [[0, 0]]
    return store
  if a % 2 != 0:
    store = [[0, 1]]
    return store


PARITY_SWITCHER = {
  'negative.negative': case_numbers_have_same_parity,
  'positive.positive': case_numbers_have_same_parity,
  '.negative': case_numbers_have_different_parity,
  'negative.': case_numbers_have_different_parity,
  '.': case_numbers_are_the_same_and_nonzero,
}


async def case_both_numbers_are_nonzero(data: Data) -> Data:
  a, b = deepcopy(data.body.interval)
  cases = [
    int(a < 0) * 'negative',
    int(b < 0) * 'negative',
  ]
  cases = '.'.join(cases)
  switcher = PARITY_SWITCHER[cases]
  intervals = await switcher(a=a, b=b)
  data.intervals = intervals
  return data


FORMAT_INTERVAL = {
  'zero.zero': case_both_numbers_are_zero,
  '.zero': case_one_number_is_zero,
  'zero.': case_one_number_is_zero,
  '.': case_both_numbers_are_nonzero,
}


async def format_interval(data: Data) -> Data:
  a, b = data.body.interval
  cases = [
    int(a == 0) * 'zero',
    int(b == 0) * 'zero',
  ]
  cases = '.'.join(cases)
  switcher = FORMAT_INTERVAL[cases]
  data = await switcher(data=data)
  return data


async def get_count_of_odd_numbers(data: Data) -> Data:
  store = []

  for interval in data.intervals:
    a, b = interval
    difference = abs(a - b)

    count = 0
    if difference % 2 == 0:
      count = floor(difference / 2)
    elif difference % 2 != 0:
      count = ceil(difference / 2)
    store.append(count)

  data.odds = sum(store)
  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)} 
    output: 
      odds: {data.odds}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data = await format_interval(data=data)
  data = await get_count_of_odd_numbers(data=data)
  data = await get_response(data=data)
  return data

#!/usr/bin/env python3

from typing import List
from dataclasses import dataclass, field, asdict
from math import floor
import yaml

from api import models


@dataclass
class Body:
  arrays: List[int] | None = None
  operations: List[List] | None = None


@dataclass
class RequestData:
  body: Body | None = None


@dataclass
class Request:
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  numbers: List[int] | None = None
  output: List[int] | None = None


async def median_finder(
  data: Data,
  i: None = None,
) -> Data:
  _ = i
  data.output = [[]]
  data.numbers = []
  return data


async def add_num(
  data: Data,
  i: int,
) -> Data:
  number = data.body.arrays[i]
  data.numbers.append(number[0])
  data.output.append([])
  return data


async def get_median_when_n_is_odd(
  numbers: List[int],
  n: int,
) -> float:
  if n > 1:
    n = n - 1
    n = int(floor(n / 2))
    median = numbers[n]
    return median

  if n == 1:
    median = numbers[0]
    return median


async def get_median_when_n_is_even(
  numbers: List[int],
  n: int,
) -> float:
  n = int(n / 2)
  m = int(n - 1)
  median = numbers[m] + numbers[n]
  median = median / 2
  return median


async def get_median_when_n_is_zero(
  numbers: List[int],
  n: int,
) -> float:
  _ = numbers, n
  median = 0
  return median


PARITY_SWITCHER = {
  'even': get_median_when_n_is_even,
  'odd': get_median_when_n_is_odd,
  '': get_median_when_n_is_zero,
}


async def find_median(
  data: Data,
  i: int,
) -> Data:
  _ = i
  n = len(data.numbers)

  parity = [
    int(n % 2 != 0) * 'odd',
    int(n % 2 == 0) * 'even',
  ]
  parity = ''.join(parity)
  switcher = PARITY_SWITCHER[parity]

  data.numbers.sort()
  median = await switcher(numbers=data.numbers, n=n)
  data.output.append([median])
  return data


OPERATION_SWITCHER = {
  'median_finder': median_finder,
  'add_num': add_num,
  'find_median': find_median,
}


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: {data.output}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> Data:
  data = Data(body=request.data.body)
  request = None

  for i, operation in enumerate(data.body.operations):
    switcher = OPERATION_SWITCHER[operation]
    data = await switcher(data=data, i=i)

  data = await get_response(data=data)
  return data

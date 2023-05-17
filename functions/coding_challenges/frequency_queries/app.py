#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List
import yaml

from api import models


@dataclass
class Body:
  queries: List[List[int]] = field(default_factory=lambda: [])


@dataclass
class RequestData:
  body: Body | None = None


@dataclass
class Request:
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  i: int = -1
  number_store: List = field(default_factory=lambda: [])
  output: List = field(default_factory=lambda: [])


async def add_number(data: Data) -> Data:
  number = data.body.queries[data.i][1]
  data.number_store.append(number)
  return data


async def remove_number(data: Data) -> Data:
  number = data.body.queries[data.i][1]
  n = len(data.number_store)
  for i in reversed(range(n)):
    if data.number_store[i] == number:
      del data.number_store[i]
      break
  return data


async def get_number_frequencies(data: Data) -> Data:
  '''Get the frequency that each number in the store appears at,
  and return 1 if the if there is a number whose frequency matches
  a specified one.'''
  frequency = data.body.queries[data.i][1]
  n = len(data.number_store)
  number_store_frequencies = {}
  # Get frequency of numbers in store
  for i in range(n):
    number = data.number_store[i]
    if number not in number_store_frequencies:
      number_store_frequencies[number] = 0
    number_store_frequencies[number] += 1
  # Check if there is a number listed at the frequency in the store
  values = list(number_store_frequencies.values())
  output = 0
  if frequency in values:
    output = 1
  data.output.append(output)
  return data


async def get_response(data: Data) -> models.Data:
  data = f'''
    input: {asdict(data.body)}
    output: {data.output}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


QUERY_SWITCHER = {
  1: add_number,
  2: remove_number,
  3: get_number_frequencies,
}


async def main(request: Request) -> Data:
  data = Data(body=request.data.body)
  request = None
  for i, query in enumerate(data.body.queries):
    data.i = i
    switcher = QUERY_SWITCHER[query[0]]
    data = await switcher(data)
  data = await get_response(data=data)
  return data

#!/usr/bin/env python3

import dataclasses as dc
from typing import List
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  queries: List[List[int]] = dc.field(default_factory=lambda: [])


@dc.dataclass
class Data:
  body: Body | None = None
  i: int = -1
  number_store: List = dc.field(default_factory=lambda: [])
  output: List = dc.field(default_factory=lambda: [])


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


async def get_response(data: Data) -> dict:
  return {'output': data.output}


QUERY_SWITCHER = {
  1: add_number,
  2: remove_number,
  3: get_number_frequencies,
}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  queries: List[List[int]] | None = None,
) -> Data:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  for i, query in enumerate(data.body.queries):
    data.i = i
    switcher = QUERY_SWITCHER[query[0]]
    data = await switcher(data)
  data = await get_response(data=data)
  return data

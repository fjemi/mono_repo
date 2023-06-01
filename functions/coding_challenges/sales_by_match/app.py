#!usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
import math
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  socks: List[List[int]] | None = None


@dc.dataclass
class MatchingPairs:
  values: Dict[int, int] | None = None
  n: int = 0


@dc.dataclass
class Data:
  body: Body | None = None
  matching_pairs: MatchingPairs | None = None


async def count_socks(data: Data) -> Data:
  store = {}
  for sock in data.body.socks:
    if sock not in store:
      store[sock] = 0
    store[sock] += 1
  data.matching_pairs = MatchingPairs(values=store)
  return data


async def get_matching_pairs(data: Data) -> Data:
  store = {}
  for key, value in data.matching_pairs.values.items():
    value = math.floor(value / 2)
    if value == 0:
      continue
    store[key] = value
  data.matching_pairs.values = store
  data.matching_pairs.n = sum(list(store.values()))
  return data


async def get_response(data: Data) -> dict:
  data = {
    'matching_paris': data.matching_pairs.values,
    'count': data.matching_pairs.n,
  }
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  socks: List[int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  data = await count_socks(data=data)
  data = await get_matching_pairs(data=data)
  data = await get_response(data=data)
  return data

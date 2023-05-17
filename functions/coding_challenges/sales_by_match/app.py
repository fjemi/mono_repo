#!usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import List, Dict
import math
import yaml

from api import models


@dataclass 
class Body(models.Body):
  socks: List[List[int]] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class MatchingPairs:
  values: Dict[int, int] | None = None
  n: int = 0


@dataclass
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


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      matching_paris: {asdict(data.matching_pairs)}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  data = await count_socks(data=data)
  data = await get_matching_pairs(data=data)
  data = await get_response(data=data)
  return data

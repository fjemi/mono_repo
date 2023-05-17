#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List
import yaml

from api import models as api_models
from functions.security.authentication import app as authentication


@dataclass
class Body(api_models.Body):
  nums: List[int] | None = None


@dataclass
class Data:
  body: Body = field(default_factory=lambda: Body())
  nums: List[int] | None = None
  triplet_indices: List[List[int]] | None = None
  triplets: List[List[int]]  | None = None


async def get_triplet_indices(data: Data) -> Data:
  store = []

  nums_n = len(data.nums)
  leaves = [str(i) for i in range(nums_n)]
  tree = [leaves]

  count = 0
  while count < 2:
    count += 1
    store = {}
    previous_branch = tree[-1]
    for branch in previous_branch:
      branch_leaves = branch.split('.')
      for leaf in leaves:
        if leaf in branch_leaves:
          continue

        next_branch = branch_leaves + [leaf]
        next_branch.sort()
        next_branch = '.'.join(next_branch)
        store[next_branch] = ''

    branches = list(store.keys())
    tree.append(branches)

  data.triplet_indices = tree[-1]
  return data


async def get_triplet_values(data: Data) -> Data:
  store = {}
  for indices in data.triplet_indices:
    indices_ints = indices.split('.')
    triplet = []
    for index in indices_ints:
      index = int(index)
      number = data.nums[index]
      triplet.append(number)
    if sum(triplet) != 0:
      continue
    triplet.sort()
    string = ''
    for number in triplet:
      string = f'{string}.{number}'
    store[string[1:]] = None
  data.triplets = list(store.keys())
  return data


async def process_triplet_values(data: Data) -> Data:
  store = []
  for triplet in data.triplets:
    triplet = triplet.split('.')
    triplet_n = len(triplet)
    for i in range(triplet_n):
      triplet[i] = int(triplet[i])
    store.append(triplet)
  data.triplets = store
  return data


async def get_response(
  data: Data,
  response: api_models.Response = api_models.Response,
) -> api_models.Response:
  data = f'''
    nums: {data.nums}
    triplets: {data.triplets}
  '''
  data = yaml.safe_load(data)
  data = response(data=data)
  return data


async def main(
  request: api_models.Request,
  data: Data = Data,
  # body: dict | Body | None = None,
) -> api_models.Response:
  data = data(nums=request.data.body.nums)
  request = None
  data = await get_triplet_indices(data=data)
  data = await get_triplet_values(data=data)
  data = await process_triplet_values(data=data)
  data = await get_response(data=data)
  return data

#!/usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import List
import yaml

from api import models


@dataclass
class Body(models.Body):
  height: List[int] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class TrappedRain:
  values: List[int] | None = None
  amount: int = 0


@dataclass
class Data:
  body: Body | None = None
  intervals: List[List[int]] | None = None
  heights: List[List[int]] | None = None
  trapped_rain: TrappedRain | None = None


async def get_intervals(data: Data) -> Data:
  store = []
  visited = []
  n = len(data.body.height)

  for i in range(n - 1):
    if i in visited:
      continue

    interval = [i]
    visited.append(i)
    max_height = data.body.height[i]

    for j in range(i + 1, n):
      preceding_height = data.body.height[j]
      interval.append(j)
      if preceding_height > max_height:
        break
      visited.append(j)

    store.append(interval)

  data.intervals = store
  return data


async def get_heights(data: Data) -> Data:
  store = []
  for interval in data.intervals:
    heights = []
    for i in interval:
      height = data.body.height[i]
      heights.append(height)
    store.append(heights)
  data.heights = store
  return data


async def no_split_required(
  heights: List[int],
  max_height_i: int,
) -> List[List[int]]:
  _ = max_height_i
  return [heights]


async def split_required(
  heights: List[int],
  max_height_i: int,
) -> List[List[int]]:
  splits = [
    heights[:max_height_i + 1],
    heights[max_height_i + 1: ],
  ]
  return splits


SPLIT_SWITCHER = {
  'equal': no_split_required,
  'nonequal': split_required,
}


async def split_heights(data: Data) -> Data:
  store = []

  for heights in data.heights:
    n = len(heights)
    if n < 3:
      continue

    max_height_i = n
    max_height = max(heights[1:-1])
    if max_height > heights[-1]:
      for i in reversed(range(n)):
        height = heights[i]
        if height == max_height:
          max_height_i = i
          break

    cases = [
      int(max_height_i == n) * 'equal',
      int(max_height_i != n) * 'nonequal',
    ]
    cases = ''.join(cases)
    switcher = SPLIT_SWITCHER[cases]
    heights = await switcher(
      heights=heights,
      max_height_i=max_height_i,
    )

    store.extend(heights)
  data.heights = store
  return data


async def get_trapped_rain(data: Data) -> Data:
  store = []

  for heights in data.heights:
    end_points = [
      heights[0],
      heights[-1],
    ]
    min_end_point = min(end_points)
    for height in heights[1:-1]:
      rain = min_end_point - height
      store.append(rain)

  data.trapped_rain = TrappedRain(
    values=store,
    amount=sum(store),
  )
  return data


async def process_heights(data: Data) -> Data:
  data = await split_heights(data=data)
  data = await get_trapped_rain(data=data)
  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      trapped_rain: {asdict(data.trapped_rain)}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


class Store:
  pass


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data = await get_intervals(data=data)
  data = await get_heights(data=data)
  data = await process_heights(data=data)
  data = await get_response(data=data)
  return data

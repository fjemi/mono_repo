#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict
import yaml

from api import models


@dataclass 
class Body(models.Body):
  times: List[int] = field(default_factory=lambda: [])
  divisor: int | float = 60


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  song_pairs: List[List[int]] = field(default_factory=lambda: [])
  divisible_pairs: List[Dict[str, List[int] | int]] = field(default_factory=lambda: [])


async def get_song_pairs(times: List[int]) -> List[List[int]]:
  store = []
  times_n = len(times)
  for i in range(times_n - 1):
    for j in range(i + 1, times_n):
      pair = [
        times[i],
        times[j],
      ]
      store.append(pair)
  return store


async def get_divisible_pairs(
  song_pairs: List[List[int]],
  divisor: int,
) -> List[List[int]]:
  store = []
  pairs_n = len(song_pairs)
  for i in range(pairs_n):
    pair = song_pairs[i]
    total_duration = sum(pair)
    check = total_duration % divisor == 0
    if check:
      data = {
        'pair': pair,
        'total_duration': total_duration,
      }
      store.append(data)
  return store


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      songs: {data.divisible_pairs}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> Data:
  data = Data(body=request.data.body)
  request = None
  data.song_pairs = await get_song_pairs(times=data.body.times)
  data.divisible_pairs = await get_divisible_pairs(
    song_pairs=data.song_pairs,
    divisor=data.body.divisor,
  )
  data = await get_response(data=data)
  return data

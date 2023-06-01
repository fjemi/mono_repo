#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  times: List[int] = dc.field(default_factory=lambda: [])
  divisor: int | float = 60


@dc.dataclass
class Data:
  body: Body | None = None
  song_pairs: List[List[int]] = dc.field(default_factory=lambda: [])
  divisible_pairs: List[Dict[str, List[int] | int]] = dc.field(default_factory=lambda: [])


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


async def get_response(data: Data) -> dict:
  return {'songs': data.divisible_pairs}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  times: List[int] | None = None,
  divisor: int | float | None = None,
) -> Data:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.song_pairs = await get_song_pairs(times=data.body.times)
  data.divisible_pairs = await get_divisible_pairs(
    song_pairs=data.song_pairs,
    divisor=data.body.divisor,
  )
  data = await get_response(data=data)
  return data

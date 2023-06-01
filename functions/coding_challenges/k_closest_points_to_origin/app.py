#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from math import sqrt
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  points: List[List[int]] | None = None
  k: int= 0


@dc.dataclass
class Data:
  body: Body | None = None
  distances_from_origin: Dict[float, List[int]] = dc.field(default_factory=lambda: {})
  closest_points: List[List[int]] = dc.field(default_factory=lambda: [])


async def get_distance_between_two_points(
  point_one: List[int],
  point_two: List[int],
) -> List[List[int]]:
  a = point_one[0] - point_two[0]
  b = point_one[1] - point_two[1]
  expression = a**2 + b**2
  return sqrt(expression)


async def get_distances_from_origin(
  points: List[List[int]],
) -> List[List[int]]:
  store = {}
  points_n = len(points)

  for i in range(points_n):
    distance = await get_distance_between_two_points(
      point_one=points[i],
      point_two=[0, 0],
    )
    store[distance] = points[i]
  return store


async def get_closest_points(
  distances_from_origin: Dict[float, List[int]],
  k: int,
) -> List[List[int]]:
  store = []

  keys = list(distances_from_origin.keys())
  keys.sort()
  keys = keys[:k]
  for key in keys:
    point = distances_from_origin[key]
    store.append(point)
  return store


async def get_response(data: Data) -> dict:
  return {'points': data.closest_points}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  points: List[List[int]] | None = None,
  k: int | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.distances_from_origin = await get_distances_from_origin(
    points=data.body.points,
  )
  data.closest_points = await get_closest_points(
    distances_from_origin=data.distances_from_origin,
    k=data.body.k,
  )
  data = await get_response(data=data)
  return data

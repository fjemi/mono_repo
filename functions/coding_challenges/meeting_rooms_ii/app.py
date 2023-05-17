#!/usr/bin/env python3


from dataclasses import dataclass, field, asdict
from typing import List, Dict
import yaml

from api import models


@dataclass 
class Body(models.Body):
  meeting_times: List[List[int]] = field(default_factory=lambda: [])


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None


CASE_MAP = {
  'overlapping': 1,
  'equals': 1,
  'disparate': 0,
  'within': 1,
}


@dataclass
class ModuleData:
  body: Body | None = None
  room_count: int = 0
  case_map: Dict[str, int] = field(default_factory=lambda: CASE_MAP)


CHECK_INTERVALS = {
  '[1, 1]': 'inside',
  '[1, 0]': 'overlap',
  '[0, 1]': 'overlap',
  '[0, 0]': 'outside',
}


async def check_intervals(
  times_one: List[int],
  times_two: List[int],
) -> str:
  range_one = list(range(times_one[0], times_one[1]))
  i, j = times_two
  cases = [
    int(i in range_one),
    int(j in range_one)
  ]
  cases = str(cases)
  result = CHECK_INTERVALS[cases]
  return result


GET_ROOM_COUNT = {
  'inside.inside': 1,
  'outside.inside': 1,  # Overlap
  'inside.outside': 1,  # Overlap
  'overlap.overlap': 1,
  'outside.outside': 0,
}


async def get_room_count_for_intervals(
  times_one: List[int],
  times_two: List[int],
) -> str:
  checks = [
    await check_intervals(
      times_one=times_one,
      times_two=times_two,
    ),
    await check_intervals(
      times_one=times_two,
      times_two=times_one,
    ),
  ]
  checks = f'{checks[0]}.{checks[1]}'
  result = GET_ROOM_COUNT[checks]
  return result


async def get_room_count(meeting_times: List[List[int]]) -> int:
  room_count = 0
  interval_n = len(meeting_times)
  for i in range(interval_n - 1):
    for j in range(1, interval_n):
      if i == j:
        continue
      room_count += await get_room_count_for_intervals(
        times_one=meeting_times[i],
        times_two=meeting_times[j],
      )
  # At least one room is needed for all meetings
  if room_count == 0:
    room_count = 1
  return room_count


async def get_response(data: ModuleData) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      rooms: {data.room_count} 
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = ModuleData(body=request.data.body)
  request = None
  data.room_count = await get_room_count(meeting_times=data.body.meeting_times)
  data = await get_response(data=data)
  return data

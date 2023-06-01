#!/usr/bin/env python3

import dataclasses as dc
from copy import deepcopy
from typing import List, Dict
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  job_difficulty: List[int] = dc.field(default_factory=lambda: [])
  days: int = 0

@dc.dataclass
class Data:
  body: Body | None = None
  jobs_n: int = 0
  jobs_by_day: Dict[int, List[int]] = dc.field(default_factory=lambda: {})
  minimum_difficultly: int = 0


async def pre_processing(data: Data) -> Data:
  data.jobs_n = len(data.body.job_difficulty)
  return data


async def get_jobs_by_day(data: Data) -> Dict[int, List[int]]:
  if data.body.days > data.jobs_n:
    return -1
  if data.body.days == data.jobs_n:
    return sum(data.body.job_difficulty)

  job_difficulty = deepcopy(data.body.job_difficulty)
  job_difficulty.sort()

  store = {}
  for i in range(data.body.days):
    job = job_difficulty[i]
    store[i] = [job]
    del job_difficulty[i]

  if job_difficulty != []:
    keys = list(store.keys())
    max_key = max(keys)
    store[max_key].extend(job_difficulty)

  return store


async def get_minimum_difficulty(
  jobs_by_day: Dict[int, List[int]],
) -> int:
  minimum_difficultly = 0
  values = list(jobs_by_day.values())
  n = len(values)
  for i in range(n):
    max_value = max(values[i])
    minimum_difficultly += max_value
  return minimum_difficultly


async def get_response(data: Data) -> dict:
  return {'minimum_difficultly': data.minimum_difficultly}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  job_difficulty: List[int] | None = None,
  days: int | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await pre_processing(data=data)
  data.jobs_by_day = await get_jobs_by_day(data=data)
  data.minimum_difficultly = await get_minimum_difficulty(
    jobs_by_day=data.jobs_by_day)
  data = await get_response(data=data)
  return data

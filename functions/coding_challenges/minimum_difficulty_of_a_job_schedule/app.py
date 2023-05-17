#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from copy import deepcopy
from typing import List, Dict
import yaml

from api import models


@dataclass 
class Body(models.Body):
  job_difficulty: List[int] = field(default_factory=lambda: [])
  days: int = 0


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None

@dataclass
class ModuleData:
  body: Body | None = None
  jobs_n: int = 0
  jobs_by_day: Dict[int, List[int]] = field(default_factory=lambda: {})
  minimum_difficultly: int = 0


async def pre_processing(data: ModuleData) -> ModuleData:
  data.jobs_n = len(data.body.job_difficulty)
  return data


async def get_jobs_by_day(data: ModuleData) -> Dict[int, List[int]]:
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


async def get_response(data: ModuleData) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      minimum_difficultly: {data.minimum_difficultly}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = ModuleData(body=request.data.body)
  request = None
  data = await pre_processing(data=data)
  data.jobs_by_day = await get_jobs_by_day(data=data)
  data.minimum_difficultly = await get_minimum_difficulty(
    jobs_by_day=data.jobs_by_day)
  data = await get_response(data=data)
  return data

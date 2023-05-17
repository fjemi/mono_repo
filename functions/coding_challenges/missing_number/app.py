#!usr/bin/env python3

from typing import List
from dataclasses import dataclass, asdict
import yaml

from api import models


@dataclass
class Body(models.Body):
  nums: List[str] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  missing_number: int | None = None


async def get_missing_number(data: Data) -> int | None:
  '''Finds the missing number in an nums'''
  data.body.nums.sort()
  n = len(data.body.nums)
  for i in range(n - 1):
    # Sequential numbers
    a = data.body.nums[i]
    b = data.body.nums[i + 1]

    # Difference between the two numbers
    difference = b - a
    if difference == 1:
      continue

    # Set missing number
    return a + 1


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)} 
    output: 
      missing_number: {data.missing_number}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data.missing_number = await get_missing_number(data=data)
  data = await get_response(data=data)
  return data

#!usr/bin/env python3

from typing import List
import dataclasses as dc
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  nums: List[str] | None = None


@dc.dataclass
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


async def get_response(data: Data) -> dict:
  return {'missing_number': data.missing_number}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  nums: List[str] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.missing_number = await get_missing_number(data=data)
  data = await get_response(data=data)
  return data

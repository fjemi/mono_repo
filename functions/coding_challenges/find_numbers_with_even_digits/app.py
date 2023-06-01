#!/usr/bin/env python3

import dataclasses as dc
from typing import List
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  nums: List[int] | None = None


@dc.dataclass
class EvenDigitNums:
  values: List[int] | None = None
  n: int = 0


@dc.dataclass
class Data:
  body: Body | None = None
  even_digit_nums: EvenDigitNums | None = None


async def get_even_digit_nums(data: Data) -> Data:
  store = []
  for number in data.body.nums:
    number = str(number)
    n = len(number)
    if n % 2 != 0:
      continue
    store.append(int(number))
  data.even_digit_nums = EvenDigitNums(
    values=store,
    n=len(store),
  )
  return data


async def get_response(data: Data) -> dict:
  return {
    'even_digit_nums': data.even_digit_nums.values,
    'count': data.even_digit_nums.n,
  }


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  nums: List[int] | None = None,
) -> Data:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await get_even_digit_nums(data=data)
  data = await get_response(data=data)
  return data

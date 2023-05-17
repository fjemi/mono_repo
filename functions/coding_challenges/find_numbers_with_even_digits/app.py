#!/usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import List
import yaml

from api import models


@dataclass
class Body:
  nums: List[int] | None = None


@dataclass
class RequestData:
  body: Body | None = None


@dataclass
class Request:
  data: RequestData | None = None


@dataclass
class EvenDigitNums:
  values: List[int] | None = None
  n: int = 0


@dataclass
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


async def get_response(data: Data) -> models.Data:
  data = f'''
    input: {asdict(data.body)}
    output: 
      even_digit_nums: {asdict(data.even_digit_nums)}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> Data:
  data = Data(body=request.data.body)
  request = None
  data = await get_even_digit_nums(data=data)
  # data = {
  #   'input': asdict(data.body),
  #   'output': {
  #     'even_digit_nums': asdict(data.even_digit_nums)
  #   }
  # }
  # data = await models.get_response(
  #   data=data,
  #   code=200,
  #   status='OK',
  # )
  data = await get_response(data=data)
  return data

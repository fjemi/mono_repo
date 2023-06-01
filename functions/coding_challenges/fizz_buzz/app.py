#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  numbers: List[int] | None = None


@dc.dataclass
class Result:
  number: int = 0
  value: str = ''


@dc.dataclass
class Data:
  body: Body | None = None
  results: List[str] = dc.field(default_factory=lambda: [])


SWITCHER = {
  'three.five': lambda number: 'fizz_buzz',
  'three.': lambda number: 'fizz',
  '.five': lambda number: 'buzz',
  '.': lambda number: str(number),
}


async def get_fizz_buzz(number: int) -> str:
  conditions = [
    int(number % 3 == 0) * 'three',
    int(number % 5 == 0) * 'five',
  ]
  conditions = '.'.join(conditions)
  switcher = SWITCHER[conditions]
  result = switcher(number=number)
  return result


async def get_response(data: Data) -> dict:
  return {'output': data.results}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  numbers: List[int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  if not isinstance(data.body.numbers, list):
    data.body.numbers = [data.body.numbers]
  for number in data.body.numbers:
    result = await get_fizz_buzz(number=number)
    data.results.append(result)
  data = await get_response(data=data)
  return data

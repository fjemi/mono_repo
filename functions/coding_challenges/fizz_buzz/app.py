#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List, Union, Dict
import yaml

from api import models


@dataclass
class Body:
  numbers: List[int] | None = None


@dataclass
class RequestData:
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Result:
  number: int = 0
  value: str = ''


@dataclass
class Props:
  body: Body | None = None
  results: List[str] = field(default_factory=lambda: [])


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


async def get_response(props: Props) -> models.Response:
  props = f'''
    input: {asdict(props.body)} 
    output: {props.results}
  '''
  props = yaml.safe_load(props)
  props = models.Response(data=props)
  return props


async def main(request: Request) -> models.Response:
  props = Props(body=request.data.body)
  request = None
  if not isinstance(props.body.numbers, list):
    props.body.numbers = [props.body.numbers]
  for number in props.body.numbers:
    result = await get_fizz_buzz(number=number)
    props.results.append(result)
  props = await get_response(props=props)
  return props

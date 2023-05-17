#!usr/bin/env python3

from typing import List, Union
from dataclasses import dataclass, field, asdict
import yaml

from api import models


@dataclass
class Body(models.Body):
  n: int | None = None


@dataclass
class RequestData(models.Data):
  body: Body = field(default_factory=lambda: Body())


@dataclass
class Request(models.Request):
  data: RequestData = field(default_factory=lambda: Data())


@dataclass
class Data:
  body: Body | None = None
  primes: List[int] = field(default_factory=lambda: [])


async def get_primes_between_two_and_n(data: Data) -> Data:
  data.primes = [2]
  if data.body.n == 2:
    return data
  # Determine remaining primes between 2 and n
  for number in range(3, data.body.n):
    number_is_prime = True
    for prime in data.primes:
      if number % prime == 0:
        number_is_prime = False
        break
    if number_is_prime is False:
      continue
    data.primes.append(number)
  return data


async def no_primes(data: Data) -> Data:
  return data


SWITCHER = {
  'n < 2': no_primes,
  'n >= 2': get_primes_between_two_and_n,
}


async def get_primes(data: Data) -> Data:
  cases = [
    int(data.body.n < 2) * 'n < 2',
    int(data.body.n >= 2) * 'n >= 2',
  ]
  cases = ''.join(cases)
  switcher = SWITCHER[cases]
  result = await switcher(data=data)
  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)} 
    output: 
      primes: {data.primes}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data = await get_primes(data=data)
  data = await get_response(data=data)
  return data

#!usr/bin/env python3

from typing import List
from dataclasses import dataclass, asdict
from copy import deepcopy
import yaml

from api import models


@dataclass
class Body(models.Body):
  numbers: List[int] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Swaps:
  numbers: List[int] | None = None
  positions: List[List[int]] | None = None
  n: int = 0


@dataclass
class Data:
  body: Body | None = None
  swaps: Swaps | None = None


async def sort_numbers_by_parity(swaps: Swaps) -> Swaps:
  for i in range(len(swaps.numbers) - 1):
    current_number = swaps.numbers[i]
    for j in range(i, len(swaps.numbers)):
      next_number = swaps.numbers[j]

      if not (current_number % 2 != 0 and next_number % 2 == 0):
        continue

      temp = swaps.numbers[i]
      swaps.numbers[i] = swaps.numbers[j]
      swaps.numbers[j] = temp
      positions = [i, j]
      swaps.positions.append(positions)

  swaps.n = len(swaps.positions)
  return swaps


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)} 
    output: 
      swaps: {asdict(data.swaps)}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  data.swaps = Swaps(numbers=deepcopy(data.body.numbers), positions=[])
  request = None
  data.swaps = await sort_numbers_by_parity(swaps=data.swaps)
  data = await get_response(data=data)
  return data

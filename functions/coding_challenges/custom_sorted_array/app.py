#!usr/bin/env python3

from typing import List
import dataclasses as dc
from copy import deepcopy
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  numbers: List[int] | None = None


@dc.dataclass
class Swaps:
  numbers: List[int] | None = None
  positions: List[List[int]] | None = None
  n: int = 0


@dc.dataclass
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


async def get_response(data: Data) -> dict:
  return {'swaps': dc.asdict(data.swaps)}


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
  data.swaps = Swaps(numbers=deepcopy(data.body.numbers), positions=[])
  request = None
  data.swaps = await sort_numbers_by_parity(swaps=data.swaps)
  data = await get_response(data=data)
  return data

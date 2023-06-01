#!usr/bin/env python3

import dataclasses as dc
from typing import List
from copy import deepcopy
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  array: List[int] | None = None


@dc.dataclass
class Inversions:
  values: List[List[int]] | None = None
  n: int = 0
  array: List[int] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  array_n: int = 0
  inversions: Inversions | None = None


@dc.dataclass
class Values:
  current: int | None = None
  next: int | None = None


async def case_array_length_less_than_two(data: Data) -> Data:
  data.inversions = Inversions()
  return data


async def case_array_length_greater_than_one(data: Data) -> Data:
  store = []
  array = deepcopy(data.body.array)

  i = 0
  while i < data.array_n - 1:
    for j in range(i, data.array_n - 1):
      value = Values(
        current=array[j],
        next=array[j + 1],
      )

      if value.current <= value.next:
        i += 1
        continue

      inversion = [j, j + 1]
      store.append(inversion)

      temp = deepcopy(value.next)
      array[j + 1] = value.current
      array[j] = temp
      i = 0
      break


  data.inversions = Inversions(
    array=array,
    n=len(store),
    values=store,
  )
  return data


SWITCH = {
  'n < 2': case_array_length_less_than_two,
  'n > 1': case_array_length_greater_than_one,
}


async def get_inversions(data: Data) -> Data:
  data.array_n = len(data.body.array)
  cases = [
    int(data.array_n < 2) * 'n < 2',
    int(data.array_n > 1) * 'n > 1',
  ]
  cases = ''.join(cases)
  function = SWITCH[cases]
  data = await function(data=data)
  return data


async def get_response(data: Data) -> dict:
  data = {'inversions': dc.asdict(data.inversions)}
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  array: List[int] | None = None,
) -> Data:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await get_inversions(data=data)
  data = await get_response(data=data)
  return data

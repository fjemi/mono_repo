#!/usr/bin/env python3

import dataclasses as dc
from copy import deepcopy
from typing import List, Dict
import math
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  nums1: List[int] = dc.field(default_factory = lambda: [])
  nums2: List[int] = dc.field(default_factory = lambda: [])


@dc.dataclass
class Data:
  body: Body | None = None
  array_copies: List[List[int]] | None = None
  array: List[int] = dc.field(default_factory = lambda: [])
  median: float | int | None = None


async def pre_processing(data: Data) -> Data:
  data.array_copies = [
    deepcopy(data.body.nums1),
    deepcopy(data.body.nums2),
  ]
  return data


async def case_nums1_equal_nums2(data: Data) -> Data:
  values = [
    data.body.nums1[0],
    data.body.nums2[0],
  ]
  data.array.extend(values)
  data.body.nums1.pop(0)
  data.body.nums2.pop(0)
  return data


async def case_nums1_greater_than_nums2(data: Data) -> Data:
  value = data.body.nums2[0]
  data.array.append(value)
  data.body.nums2.pop(0)
  return data


async def case_nums1_less_than_nums2(data: Data) -> Data:
  value = data.body.nums1[0]
  data.array.append(value)
  data.body.nums1.pop(0)
  return data


async def case_nums1_empty(data: Data) -> Data:
  data.array.extend(data.body.nums2)
  data.body.nums2 = []
  return data


async def case_nums2_empty(data: Data) -> Data:
  data.array.extend(data.body.nums1)
  data.body.nums1 = []
  return data


async def case_nums1_and_nums2_empty(data: Data) -> Data:
  return data


async def case_nums1_and_nums2_values(
  data: Data,
  _locals: Dict = locals(),
) -> Data:
  a = data.body.nums1[0]
  b = data.body.nums2[0]

  cases = {
    a == b: 'equals',
    a < b: 'less_than',
    a > b: 'greater_than',
  }
  _case = cases[1]
  function_name = f'case_nums1_{_case}_nums2'
  function = _locals[function_name]
  result = await function(data=data)
  return result


# Switcher
GET_MERGED_ARRAY= {
  '[0, 0]': case_nums1_and_nums2_empty,
  '[0, 1]': case_nums1_empty,
  '[1, 0]': case_nums2_empty,
  '[1, 1]': case_nums1_and_nums2_values,
}


async def get_merged_array(data: Data) -> Data:
  # Process the values of 'nums1' and 'nums2' until both arrays are empty
  while [len(data.body.nums2), len(data.body.nums1)] != [0, 0]:
    conditions = [
      int(len(data.body.nums1) != 0),
      int(len(data.body.nums2) != 0),
    ]
    conditions = f'{conditions}'
    switcher = GET_MERGED_ARRAY[conditions]
    data = await switcher(data=data)
  return data


async def post_processing(data: Data) -> Data:
  data.body.nums1 = data.array_copies[0]
  data.body.nums2 = data.array_copies[1]
  data.array_copies = None
  return data


async def case_median_array_length_zero(
  array: List[int],
  n: int,
) -> int | float:
  _ = array, n
  return 0


async def case_median_array_length_one(
  array: List[int],
  n: int
) -> float | int:
  _ = n
  return array[1]


async def case_median_array_length_odd(
  array: List[int],
  n: int,
) -> int | float:
  a = math.floor(n / 2)
  return array[a]


async def case_median_array_length_even(
  array: List[int],
  n: int,
) -> int | float:
  a = n / 2
  a = math.floor(a)
  b = a - 1
  return (array[a] + array[b]) / 2


GET_MEDIAN = {
  '[1, 0, 1, 0]': case_median_array_length_zero,
  '[0, 1, 0, 1]': case_median_array_length_one,
  '[0, 0, 1, 0]': case_median_array_length_even,
  '[0, 0, 0, 1]': case_median_array_length_odd,
}


async def get_median(array: List[int]) -> float | int:
  n = len(array)
  conditions = [
    int(n == 0),
    int(n == 1),
    int(n % 2 == 0),
    int(n % 2 != 0),
  ]
  conditions = f'{conditions}'
  switcher = GET_MEDIAN[conditions]
  result = await switcher(array=array, n=n)
  return result

async def get_response(data: Data) -> dict:
  return {'median': data.median}


# pylint: disable=unused-argument
async def main(request: Request | None = None,
  nums1: List[int] | None = None,
  nums2: List[int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await pre_processing(data=data)
  data = await get_merged_array(data=data)
  data.median = await get_median(array=data.array)
  data = await post_processing(data=data)
  data = await get_response(data=data)
  return data

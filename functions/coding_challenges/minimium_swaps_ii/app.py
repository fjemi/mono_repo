#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Any, Dict
from copy import deepcopy
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  array: List[int] | None = None


@dc.dataclass
class Element:
  value: Any | None = None
  position: int | None = None


@dc.dataclass
class Swap:
  a: Element | None = None
  b: Element | None = None


@dc.dataclass
class Elements:
  values: List[int] = dc.field(default_factory=lambda: [])
  positions: List[int] = dc.field(default_factory=lambda: [])


@dc.dataclass
class Data:
  body: Body | None = None
  swaps: List[Swap] = dc.field(default_factory=lambda: [])
  arrays_with_swaps: List[List[int]] = dc.field(default_factory=lambda: [])
  ordered_array: List[int] | None = None
  swap_count: int = 0


async def get_differences_between_values_and_positions(
  array: List[int],
) -> Dict[int, Elements]:
  min_value = min(array)
  store = {}
  n = len(array)
  for i in range(n):
    value = array[i]
    # difference = min_value - abs(i - value)
    difference = min_value - (value - i)
    if difference not in store.keys():
      store[difference] = Elements()
    # Add position/value to differences store
    store[difference].values.append(value)
    store[difference].positions.append(i)
  return store


async def get_values_and_positions_to_swap(
  differences: Dict[int, Elements],
) -> Swap | None:

  # Get the min and max difference values
  keys = list(differences.keys())
  min_difference = min(keys)
  max_difference = max(keys)

  # Numbers are in order if min/max differences are the same
  if min_difference == max_difference:
    return

  # Max values from the lists of min/max numbers need to be swapped
  max_numbers = differences[max_difference]
  min_numbers = differences[min_difference]
  value_a = max(max_numbers.values)
  value_b = max(min_numbers.values)
  index_a = max_numbers.values.index(value_a)
  index_b = min_numbers.values.index(value_b)
  position_a = max_numbers.positions[index_a]
  position_b = min_numbers.positions[index_b]

  return Swap(
    a=Element(value=value_a, position=position_a),
    b=Element(value=value_b, position=position_b),
  )


async def get_array_withed_swapped_values(
  array: List[int],
   swap: Swap,
) -> List[int]:
  if swap is None:
    return 
  array = deepcopy(array)
  array[swap.a.position] = swap.b.value
  array[swap.b.position] = swap.a.value
  return array


async def post_processing(data: Data) -> Data:
  data.ordered_array = data.arrays_with_swaps[-1]
  data.swap_count = len(data.swaps) - 1
  data.ordered_array = data.arrays_with_swaps[-2]
  return data


async def get_ordered_array(data: Data) -> Data:
  while None not in data.swaps:
    array = data.arrays_with_swaps[-1]
    differences = await get_differences_between_values_and_positions(
      array=array)
    swap = await get_values_and_positions_to_swap(differences=differences)
    data.swaps.append(swap)
    array = await get_array_withed_swapped_values(array=array, swap=swap)
    data.arrays_with_swaps.append(array)
  return data


async def get_response(data: Data) -> dict:
  return {'swap_count': data.swap_count}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  array: List[int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.arrays_with_swaps.append(data.body.array)
  data = await get_ordered_array(data=data)
  data = await post_processing(data=data)
  data = await get_response(data=data)
  return data

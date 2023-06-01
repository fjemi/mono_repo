#!/usr/bin/env python3

import dataclasses as dc
from typing import List
from copy import deepcopy
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  string: str = ''


@dc.dataclass
class Chars:
  indices: dict = dc.field(default_factory=lambda: {})
  ordered: str = ''


@dc.dataclass
class Bounds:
  lower: int = 0
  upper: int = 0


@dc.dataclass
class Partitions:
  indices: List[Bounds] = dc.field(default_factory=lambda: [])
  values: List[str] = dc.field(default_factory=lambda: [])
  sizes: List[int] = dc.field(default_factory=lambda: [])


@dc.dataclass
class Data:
  body: Body | None = None
  chars: Chars | None = None
  partitions: Partitions = dc.field(default_factory=lambda: Partitions())
  bounds: Bounds | None = None


async def get_ordered_chars_and_indices(string: str) -> Chars:
  chars = Chars()
  for i in range(len(string)):
    # Get the indices of chars
    char = string[i]
    if char not in chars.indices:
      chars.indices[char] = []
    chars.indices[char].append(i)
    # Place chars in the order they are last visited
    position = chars.ordered.find(char)
    if position != -1:
      chars.ordered = chars.ordered[:position] + chars.ordered[position + 1:]
    chars.ordered = chars.ordered + char
  return chars


async def case_lower_upper_in_bounds(
  data: Data,
  upper: int,
  lower: int
) -> Data:
  return data


async def case_upper_in_bounds(
  data: Data,
  upper: int,
  lower: int
) -> Data:
  data.bounds.lower = lower
  return data


async def case_lower_upper_not_in_bounds(
  data: Data,
  upper: int,
  lower: int
) -> Data:
  data.partitions.indices.append(deepcopy(data.bounds))
  data.bounds.lower = lower
  data.bounds.upper = upper
  return data


SWITCH = {
  'lower.upper': case_lower_upper_in_bounds,
  '.upper': case_upper_in_bounds,
  '.': case_lower_upper_not_in_bounds,
}


async def get_partition_indices(data: Data) ->  Data:
  data.partitions = Partitions()

  char = data.chars.ordered[-1]
  data.bounds = Bounds(
    upper=max(data.chars.indices[char]),
    lower=min(data.chars.indices[char]),
  )

  for char in reversed(data.chars.ordered[:-1]):
    upper = max(data.chars.indices[char])
    lower = min(data.chars.indices[char])
    cases = [
      int(lower > data.bounds.lower) * 'lower',
      int(upper > data.bounds.lower) * 'upper',
    ]
    cases = '.'.join(cases)
    switch = SWITCH[cases]
    data = await switch(data=data, upper=upper, lower=lower)
  data.partitions.indices.append(data.bounds)
  return data


async def get_partition_strings_and_sizes(
  partitions: Partitions,
  string: str,
) -> Partitions:
  for bounds in partitions.indices:
    partition_string = string[bounds.lower:bounds.upper + 1]
    partitions.values.append(partition_string)
    partitions.sizes.append(len(partition_string))
  return partitions


async def get_response(data: Data) -> dict:
  data = {
    'sizes': data.partitions.sizes,
    'partitions': data.partitions.values,
  }
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  string: str | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.chars = await get_ordered_chars_and_indices(
    string=data.body.string)
  data = await get_partition_indices(data=data)
  data.partitions = await get_partition_strings_and_sizes(
    string=data.body.string,
    partitions=data.partitions,
  )
  data = await get_response(data=data)
  return data

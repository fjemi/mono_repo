#!usr/bin/env python3

from typing import Dict, List
from math import ceil
import dataclasses as dc
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  string: str = ''


@dc.dataclass
class Data:
  body: Body | None = None
  char_counts: Dict[str, int] = dc.field(default_factory=lambda: {})
  count_upper_bound: int = -1
  char_counts_check: bool = True
  reorganized_string: str | None = None


async def get_char_counts(string: str) -> Dict[str, int]:
  store = {}
  for char in string:
    if char not in store:
      store[char] = 0
    store[char] += 1
  return store


async def get_upper_bound(string: str) -> int:
  n = len(string)
  if n == 0:
    return 0

  parity = n % 2 == 0
  # Bounds for parity, even or odd number, of chars
  upper_bound_mapper = {
    1: n / 2 + 1,
    0: ceil((n / 2) + 1),
  }
  return upper_bound_mapper[parity]


async def check_char_counts_values(
  count_upper_bound: int,
  char_count_values: List[int],
) -> bool:
  n = sum(char_count_values)
  # Check if any char occurrences exceed the upper bound
  for value in char_count_values:
    if value >= count_upper_bound:
      return False
  return True


async def get_reorganized_string(
  string: str,
  char_counts_check: bool,
  char_counts: List[int],
) -> str:
  if char_counts_check is False:
    return None
  if string == '':
    return ''

  store = {}
  keys = char_counts.keys()
  for char in keys:
    value = char_counts[char]
    if value not in store:
      store[value] = []
    store[value].append(char)

  counts = list(store.keys())
  counts.sort(reverse=True)

  reorganized_string = ''
  for i in range(counts[0]):
    for count in counts:
      if i >= count:
        continue
      chars = store[count]
      for char in chars:
        reorganized_string = reorganized_string + char

  # Handle cases where reorganized string and string are the same.abs
  # Reverse the reorganized string
  if string == reorganized_string:
    reorganized_string = reorganized_string[::-1]

  return reorganized_string


async def get_response(data: Data) -> dict:
  return {'reorganized_string': data.reorganized_string}


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
  data.char_counts = await get_char_counts(string=data.body.string)
  data.count_upper_bound = await get_upper_bound(string=data.body.string)
  data.char_counts_check = await check_char_counts_values(
    count_upper_bound=data.count_upper_bound,
    char_count_values=list(data.char_counts.values())
  )
  data.reorganized_string = await get_reorganized_string(
    string=data.body.string,
    char_counts_check=data.char_counts_check,
    char_counts=data.char_counts,
  )
  data = await get_response(data=data)
  return data

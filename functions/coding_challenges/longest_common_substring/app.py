#!usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
import math
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  str1: str | None = None
  str2: str | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  substrings: Dict[str, List[str]] | None = None
  common_substrings: Dict[int, List[str]] | None = None


async def get_substrings_of_size_n(
  string: str,
  n: int,
  i: int,
  substrings: List[str],
) -> List[str]:
  windows = n / (n - i)
  windows = math.ceil(windows)
  for count in range(windows):
    substring = string[0 + count:i + count]
    substrings.append(substring)
  return substrings


async def get_substrings(data: Data) -> Data:
  store = {}

  names = ['str1', 'str2']
  for name in names:
    string = getattr(data.body, name)
    n = len(string)

    substrings = []
    for i in range(n):
      substrings =await get_substrings_of_size_n(
        string=string,
        n=n,
        i=i,
        substrings=substrings,
      )
    store[string] = substrings

  data.substrings = store
  return data


async def get_common_substrings(data: Data) -> Data:
  store = {}
  a, b = list(data.substrings.values())
  for substring in a:
    if substring not in b:
      continue
    n = len(substring)
    if n not in store:
      store[n] = []
    store[n].append(substring)
  data.common_substrings = store
  return data


async def get_response(data: Data) -> dict:
  return {'common_substrings': data.common_substrings}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  str1: str | None = None,
  str2: str | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await get_substrings(data=data)
  data = await get_common_substrings(data=data)
  data = await get_response(data=data)
  return data

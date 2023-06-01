#!usr/bin/env python3

import dataclasses as dc
from typing import List
from fastapi import Request


from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  string: str = ''


@dc.dataclass
class Data:
  body: Body | None = None
  alternating_char_positions: List[int] = dc.field(default_factory=lambda: [])
  deletions_count: int = 0


async def get_alternating_char_positions(string) -> List[int]:
  store = []
  # Handle empty string
  if len(string) == 0:
    return store

  # Handle non-empty strings
  store.append(0)
  # Add non repeating chars to store
  n = len(string)
  for i in range(1, n):
    # Repeating char
    index = store[-1]
    char = string[index]
    if char == string[i]:
      continue
    store.append(i)
  return store


async def get_deletions_count(data: Data) -> int:
  m = len(data.body.string)
  n = len(data.alternating_char_positions)
  return m - n


async def get_response(data: Data) -> dict:
  return {'deletions': data.deletions_count}


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
  data.alternating_char_positions = await get_alternating_char_positions(
    string=data.body.string)
  data.deletions_count = await get_deletions_count(data=data)
  data = await get_response(data=data)
  return data

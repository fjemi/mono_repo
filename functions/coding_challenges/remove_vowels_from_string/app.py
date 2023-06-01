#!usr/bin/env python3

import dataclasses as dc
from typing import List
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']


@dc.dataclass
class Body:
  string: str = ''


@dc.dataclass
class Data:
  body: Body | None = None
  vowels: List[str] = dc.field(default_factory=lambda: VOWELS)
  vowel_positions: List[str] = dc.field(default_factory=lambda: [])
  modified_string: str = ''


async def get_vowel_positions(string: str, vowels: List[str]) -> List[int]:
  string = string.lower()
  store = []
  n = len(string)
  for i in range(n):
    char = string[i]
    if char not in vowels:
      continue
    store.append(i)
  return store


async def remove_vowels_from_string(string: str, vowel_positions: List[str]) -> str:
  store = []
  n = len(string)
  for i in range(n):
    if i in vowel_positions:
      continue
    char = string[i]
    store.append(char)
  return ''.join(store)


async def get_response(data: Data) -> dict:
  return {'modified_string': data.modified_string}


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
  data.vowel_positions = await get_vowel_positions(
    string=data.body.string,
    vowels=data.vowels,
  )
  data.modified_string = await remove_vowels_from_string(
    string=data.body.string,
    vowel_positions=data.vowel_positions,
  )
  data = await get_response(data=data)
  return data

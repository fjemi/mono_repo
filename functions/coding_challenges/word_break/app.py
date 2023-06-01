#!/usr/bin/env python3

import dataclasses as dc
from typing import List
from copy import deepcopy
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  string: str = ''
  word_dict: List[str] = dc.field(default_factory=lambda: [])


@dc.dataclass
class Copies:
  string: str = ''
  word_dict: List[str] = dc.field(default_factory=lambda: [])


@dc.dataclass
class Data:
  body: Body | None = None
  copies: Copies | None = None
  current_word: str = ''
  segments: List[str] = dc.field(default_factory=lambda: [])


async def pre_processing(data: Data) -> Data:
  data.copies = Copies(
    string = deepcopy(data.body.string),
    word_dict = deepcopy(data.body.word_dict),
  )
  return data


async def case_word_not_at_zero(
  data: Data,
) -> Data:
  # Do nothing
  return data


async def case_word_not_in_string(
  data: Data,
) -> Data:
  # Delete the word from word dict
  i = data.body.word_dict.index(data.current_word)
  del data.body.word_dict[i]
  return data


async def case_word_at_zero(
  data: Data,
) -> Data:
  # Add the word as a segment and remove it from
  # the string
  data.segments.append(data.current_word)
  word_n = len(data.current_word)
  data.body.string = data.body.string[word_n:]
  return data


async def get_string_segments(data: Data) -> Data:
  _continue = True
  while _continue:
    # Conditions to exit loop
    conditions = [
      data.body.string == '',
      data.body.word_dict == [],
    ]
    if sum(conditions) != 0:
      _continue = False
      break

    # Store segments of words at position zero of
    # the string and remove word from string
    for word in data.body.word_dict:
      data.current_word = word
      position = data.body.string.find(
        data.current_word)
      cases = {
        position == 0: case_word_at_zero,
        position == -1: case_word_not_in_string,
        position not in [0, -1]: case_word_not_at_zero,
      }
      function = cases[1]
      data = await function(data=data)

  # String cannot be fully segmented
  # with words from the dictionary
  if data.body.string != '':
    data.segments = []

  return data


async def get_response(data: Data) -> dict:
  return {'segments': data.segments}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  string: str | None = None,
  word_dict: List[str] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  data = await pre_processing(data=data)
  data = await get_string_segments(data=data)
  data = await get_response(data=data)
  return data

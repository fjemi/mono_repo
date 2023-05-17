#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import List
from copy import deepcopy
import yaml

from api import models


@dataclass 
class Body(models.Body):
  string: str = ''
  word_dict: List[str] = field(default_factory=lambda: [])


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None


@dataclass
class Copies:
  string: str = ''
  word_dict: List[str] = field(default_factory=lambda: [])


@dataclass
class ModuleData:
  body: Body | None = None
  copies: Copies | None = None
  current_word: str = ''
  segments: List[str] = field(default_factory=lambda: [])


async def pre_processing(data: ModuleData) -> ModuleData:
  data.copies = Copies(
    string = deepcopy(data.string),
    word_dict = deepcopy(data.word_dict),
  )
  return data


async def case_word_not_at_zero(
  data: ModuleData,
) -> ModuleData:
  # Do nothing
  return data


async def case_word_not_in_string(
  data: ModuleData,
) -> ModuleData:
  # Delete the word from word dict
  i = data.word_dict.index(data.current_word)
  del data.word_dict[i]
  return data


async def case_word_at_zero(
  data: ModuleData,
) -> ModuleData:
  # Add the word as a segment and remove it from
  # the string
  data.segments.append(data.current_word)
  word_n = len(data.current_word)
  data.string = data.string[word_n:]
  return data


async def get_string_segments(data: ModuleData) -> ModuleData:
  _continue = True
  while _continue:
    # Conditions to exit loop
    conditions = [
      data.string == '',
      data.word_dict == [],
    ]
    if sum(conditions) != 0:
      _continue = False
      break

    # Store segments of words at position zero of
    # the string and remove word from string
    for word in data.word_dict:
      data.current_word = word
      position = data.string.find(
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
  if data.string != '':
    data.segments = []

  return data


async def get_response(data: ModuleData) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      sentences: {data.sentences}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(data: ModuleData | dict | str) -> models.Response:
  data = ModuleData(body=request.data.body)
  data = await pre_processing(data=data)
  data = await get_string_segments(data=data)
  data = await get_response(data=data)
  return data

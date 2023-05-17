#!/usr/bin/env python3

import string
from random import randint, shuffle
from dataclasses import dataclass, field, asdict
from typing import List, Dict
import yaml

from api import models


@dataclass
class Body(models.Body):
  required_chars: List[str] = field(default_factory=lambda: [])
  length: int = 8


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


CHARS = {
  'lowercase': string.ascii_lowercase,
  'uppercase': string.ascii_uppercase,
  'number': string.digits,
  'special': string.punctuation
}


@dataclass
class Data:
  body: Body | None = None
  chars: Dict[str, List[str]] = field(default_factory=lambda: CHARS)
  counts: Dict = field(default_factory=lambda: {})
  char_positions: List[int] = field(default_factory=lambda: [])
  password: str = ''


async def get_char_counts(data: Data) -> dict:
  '''Returns the percentage of occurance of char types in the total
  of available chars'''
  counts = {}
  keys = list(data.chars.keys())
  for key in keys:
    n = len(data.chars[key])
    counts[key] = n
  return counts


async def set_char_positions(data: Data) -> List[int]:
  '''Returns a list of integers representing the position of char types
  in the password to generate'''
  store = []
  keys = list(data.chars.keys())
  keys_n = len(keys)

  if keys_n == 0:
    return store

  # Shuffle required chars
  shuffle(data.body.required_chars)
  # Set required char types
  for chars in data.body.required_chars:
    if chars not in keys:
      continue
    position = keys.index(chars)
    store.append(position)

  # Randomly add remaining char types to list
  n = data.body.length - len(store)
  if n == 0:
    return store

  for i in range(n):
    # Insert random char type into random position
    m = len(store)
    position = randint(0, m)
    chars = randint(0, keys_n - 1)
    store.insert(position, chars)

  return store


async def get_password(data: Data) -> str:
  '''Returns a reandomly generated password from a list of char type positions.
  '''
  store = []
  keys = list(data.chars.keys())
  for position in data.char_positions:
    # Char type and number of chars
    key = keys[position]
    count = data.counts[key]
    # Get the random char at a position form char type
    position = randint(0, count - 1)
    char = data.chars[key][position]
    store.append(char)
  password = ''.join(store)
  return password


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      password: {data.password}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data.counts = await get_char_counts(data)
  data.char_positions = await set_char_positions(data)
  data.password = await get_password(data)
  data = await get_response(data=data)
  return data

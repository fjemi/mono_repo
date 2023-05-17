#!usr/bin/env python3

from typing import List, Dict
from dataclasses import dataclass, field, asdict
from copy import deepcopy
import yaml

from api import models


@dataclass
class Body(models.Body):
  string: str | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  decompressed_string: str = ''
  expanded_brackets: List[Dict] = field(default_factory=lambda: [])


async def get_bracket_indices(string: str) -> List[int]:
  store = []
  n = len(string)
  for i in reversed(range(n)):
    if string[i] != '[':
      continue
    store.append(i)

    for j in range(i, n):
      if string[j] == ']':
        store.append(j)
        return store
  return store


async def get_bracket_multiplier(string: str, bracket_indices: List[int]) -> str:
  if len(bracket_indices) == 0:
    return ''

  end = bracket_indices[0]
  substring = string[:end]
  n = len(substring)
  index = n
  for i in reversed(range(n)):
    char = substring[i]
    if char in ['[', ']'] or char.isalpha() is True:
      index = i + 1
      break
    index = i

  return substring[index:n]


async def get_expanded_bracket(
  string: str,
  bracket_indices: List[int],
  bracket_multiplier: str,
) -> Dict[str, str]:
  store = {}

  # Handle no brackets in the string
  if len(bracket_indices) == 0:
    store[''] = ''
    return store

  # Handle no multiplier for the brackets
  substring = string[bracket_indices[0]:bracket_indices[1] + 1]
  if bracket_multiplier == '':
    store[substring] = substring
    return store

  # Handle bracket with multiplier
  key = f'{bracket_multiplier}{substring}'
  bracket_multiplier = int(bracket_multiplier)
  value = bracket_multiplier * substring[1:-1]
  store[key] = value
  return store


async def get_string_with_replaced_bracket(
  string: str, 
  expanded_bracket: Dict[str, str],
) -> str:
  for key, value in expanded_bracket.items():
    return string.replace(key, value)


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)} 
    output: 
      decompressed_string: {data.decompressed_string}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data.decompressed_string = deepcopy(data.body.string)

  while True:
    bracket_indices = await get_bracket_indices(string=data.decompressed_string)
    if not bracket_indices:
      break

    bracket_multiplier = await get_bracket_multiplier(
      string=data.decompressed_string,
      bracket_indices=bracket_indices,
    )
    expanded_bracket = await get_expanded_bracket(
      string=data.decompressed_string,
      bracket_indices=bracket_indices,
      bracket_multiplier=bracket_multiplier,
    )
    data.expanded_brackets.append(expanded_bracket)
    data.decompressed_string = await get_string_with_replaced_bracket(
      string=data.decompressed_string,
      expanded_bracket=expanded_bracket,
    )

  data = await get_response(data=data)
  return data

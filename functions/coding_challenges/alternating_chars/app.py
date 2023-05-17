#!usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List
import yaml

from api import models


@dataclass
class Body:
  string: str = ''


@dataclass
class Data:
  body: Body = field(default_factory=lambda: Body())


@dataclass
class Request(models.Request):
  data: Data = field(default_factory=lambda: Data())


@dataclass
class Props:
  body: Body | None = None
  alternating_char_positions: List[int] = field(default_factory=lambda: [])
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


async def get_deletions_count(props: Props) -> int:
  m = len(props.body.string)
  n = len(props.alternating_char_positions)
  return m - n


async def get_response(props: Props) -> models.Response:
  props = f'''
    input: {asdict(props.body)} 
    output:
      deletions: {props.deletions_count}
  '''
  props = yaml.safe_load(props)
  props = models.Response(data=props)
  return props


async def main(request: Request) -> models.Response:
  props = Props(body=request.data.body)
  request = None
  props.alternating_char_positions = await get_alternating_char_positions(string=props.body.string)
  props.deletions_count = await get_deletions_count(props=props)
  props = await get_response(props=props)
  return props

#!usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List
import yaml

from api import models


VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']


@dataclass
class Body(models.Body):
  string: str = ''


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  vowels: List[str] = field(default_factory=lambda: VOWELS)
  vowel_positions: List[str] = field(default_factory=lambda: [])
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


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      modifiel_string: {data.modified_string}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
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

#!/usr/bin/env python3

from dataclasses import dataclass, asdict
import yaml

from api import models


@dataclass
class Body(models.Body):
  magazine: str = ''
  note: str = ''
  case_sensitive: bool = True


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  magazine_contains_note: bool = False


async def check_magazine_contains_note(data: Data) -> bool:
  if data.body.case_sensitive is False:
    data.body.magazine = data.body.magazine.lower()
    data.body.note = data.body.note.lower()
  # Check if the magazine has each word within the note
  words = data.body.note.split(' ')
  for word in words:
    if data.body.magazine.find(word) == -1:
      return False
    data.body.magazine.replace(word, '')
  return True


async def get_response(data: Data) -> models.Response:
  props = f'''
    input: {asdict(data.body)} 
    output:
      magazine_contains_note: {data.magazine_contains_note}
  '''
  props = yaml.safe_load(props)
  props = models.Response(data=props)
  return props


async def main(request: Request) -> models.Response:
  body = asdict(request.data.body)
  body = Body(**body)
  data = Data(body=body)
  request = None
  data.magazine_contains_note = await check_magazine_contains_note(data=data)
  data = await get_response(data=data)
  return data

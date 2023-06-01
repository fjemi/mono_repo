#!/usr/bin/env python3

import dataclasses as dc
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  magazine: str = ''
  note: str = ''
  case_sensitive: bool = True


@dc.dataclass
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


async def get_response(data: Data) -> dict:
  return {'magazine_contains_note': data.magazine_contains_note}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  magazine: str | None = None,
  note: str | None = None,
  case_sensitive: bool | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.magazine_contains_note = await check_magazine_contains_note(data=data)
  data = await get_response(data=data)
  return data

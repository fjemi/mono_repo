#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Any
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  array: List[Any] | None = None
  rotations: int = 0


@dc.dataclass
class Data:
  body: Body | None = None
  rotated_array: List[Any] | None = None


async def get_rotated_array(data: Data) -> List[Any]:
  array = data.body.array
  for i in range(data.body.rotations):
    _ = i
    # Remove the first element from list and add it to end
    first_item = array[0]
    array.pop(0)
    array.append(first_item)
  data.rotated_array = get_rotated_array
  return array


async def get_response(data: Data) -> dict:
  return {'rotated_array': data.rotated_array}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  body: Body | None = None,
  rotated_array: List[Any] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.rotated_array = await get_rotated_array(data=data)
  data = await get_response(data=data)
  return data

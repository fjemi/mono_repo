#!/usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import List, Any
import yaml

from api import models


@dataclass
class Body(models.Body):
  array: List[Any] | None = None
  rotations: int = 0


@dataclass
class RequestData(models.Data):
  body: Body | None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
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


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      rotated_array: {data.rotated_array}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data.rotated_array = await get_rotated_array(data=data)
  data = await get_response(data=data)
  return data

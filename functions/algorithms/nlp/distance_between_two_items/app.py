#!/usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import List
import yaml

from api import models


@dataclass
class Body(models.Body):
  item_1: List | str | None = None
  item_2: List | str | None = None
  preserve_order: bool = False


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Difference:
  modifications: int = 0
  percentage: float = 0


@dataclass
class Data:
  body: Body | None = None
  ordered: bool = True
  difference: Difference | None = None


async def format_items(
  item_1: List[str] | str,
  item_2: List[str] | str,
  preserve_order: bool,
) -> List[str]:
  items = [item_1, item_2]
  store = []

  for item in items:
    if not isinstance(item, list):
      chars = []
      for char in item:
        chars.append(char)
      item = chars

    if not preserve_order:
      item.sort()

    store.append(item)
  return store


async def get_difference_between_items(
  items: List[str],
) -> Difference:

  n = [len(item) for item in items]
  padding = abs(n[0] - n[1]) * ['']
  index = n.index(min(n))
  items[index].extend(padding)

  modifications = 0
  max_n = max(n)
  for i in range(max_n):
    if items[0][i] == items[1][i]:
      continue
    modifications += 1

  percentage = round(modifications / max_n, 2)
  difference = Difference(
    modifications=modifications,
    percentage=percentage,
  )
  return difference


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      difference: {asdict(data.difference)}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  body = Body(**asdict(request.data.body))
  data = Data(body=body)
  request = None
  items = await format_items(
    item_1=data.body.item_1,
    item_2=data.body.item_2,
    preserve_order=data.body.preserve_order,
  )
  data.difference = await get_difference_between_items(items=items)
  data = await get_response(data=data)
  return data

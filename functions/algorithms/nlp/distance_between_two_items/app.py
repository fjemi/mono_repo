#!/usr/bin/env python3

import dataclasses as dc
from typing import List
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  item_1: List | str | None = None
  item_2: List | str | None = None
  preserve_order: bool = False


@dc.dataclass
class Difference:
  modifications: int = 0
  percent: float = 0


@dc.dataclass
class Data:
  body: Body | None = None
  call_method: str = 'module'
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

  percent = round(modifications / max_n, 2)
  difference = Difference(
    modifications=modifications,
    percent=percent,
  )
  return difference


async def get_response(data: Data) -> dict:
  data = {'difference': dc.asdict(data.difference)}
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  item_1: List | str | None = None,
  item_2: List | str | None = None,
  preserve_order: bool | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  items = await format_items(
    item_1=data.body.item_1,
    item_2=data.body.item_2,
    preserve_order=data.body.preserve_order,
  )
  data.difference = await get_difference_between_items(items=items)
  data = await get_response(data=data)
  return data

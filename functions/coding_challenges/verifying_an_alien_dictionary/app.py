#!/usr/bin/env python3

import dataclasses as dc
from typing import List
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  words: List[str] = dc.field(default_factory=lambda: [])
  order: str =  ''


@dc.dataclass
class Data:
  body: Body | None = None
  output: bool = True


async def get_word_combinations(words: List[str]) -> List[List[str]]:
  store = []
  n = len(words)
  for i in range(n):
    for j in range(i + 1, n):
      store.append([
        words[i],
        words[j],
      ])
  return store


async def get_char_orders(
  words: List[str],
  order: str,
) -> List[int]:
  words_n = [len(words[0]), len(words[1])]
  max_n = max(words_n)
  char_orders = [[], []]
  for i in range(max_n):
    char_order = -1
    if i < words_n[0]:
      char = words[0][i]
      char_order = order.find(char)
    char_orders[0].append(char_order)

    char_order = -1
    if i < words_n[1]:
      char = words[1][i]
      char_order = order.find(char)
    char_orders[1].append(char_order)
  return char_orders


async def check_char_orders(char_orders: List[List[int]]) -> bool:
  in_order = None
  char_orders_range = range(len(char_orders[0]))
  for i in char_orders_range:
    a = int(char_orders[0][i])
    b = int(char_orders[1][i])
    if a == b:
      continue
    if a < b:
      in_order = True
      break
    if a > b:
      in_order = False
      break
  return in_order


async def get_response(data: Data) -> dict:
  return {'output': data.output}


# pylint: disable=unused-argument
async def main(request: Request | None = None,
  words: List[str] | None = None,
  order: str | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  word_combinations = await get_word_combinations(
    words=data.body.words)
  checks = []
  for words in word_combinations:
    char_orders = await get_char_orders(
      words=words,
      order=data.body.order,
    )
    check = await check_char_orders(char_orders=char_orders)
    checks.append(check)
  if False in checks:
    data.output = False
  data = await get_response(data=data)
  return data

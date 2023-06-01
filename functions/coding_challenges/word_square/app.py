#!/usr/bin/env python3

import dataclasses as dc
from typing import List
import itertools
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  sequence: List[str] | None = None


@dc.dataclass
class WordSquares:
  values: List[List[str]] | None = None
  n: int = 0


@dc.dataclass
class Data:
  body: Body | None = None
  permutations: List[List[str]] | None = None
  word_squares: WordSquares | None = None


async def get_permutations(sequence: List[str]) -> int:
  store = []
  n = len(sequence[0])
  store = itertools.permutations(sequence, n)
  store = list(store)
  return store


async def check_permutations_for_squares(data: Data) -> Data:
  store = []
  n = len(data.body.sequence[0])

  for permutation in data.permutations:
    square = True
    for i in range(n):
      for j in range(n):
        char_a = permutation[i][j]
        char_b = permutation[j][i]
        if char_a != char_b:
          square = False
          break
      if not square:
        break
    if square:
      store.append(list(permutation))

  data.word_squares = WordSquares(values=store, n=len(store))
  data.permutations = None
  return data


async def get_response(data: Data) -> dict:
  data = {
    'word_squares': data.word_squares.values,
    'count': data.word_squares.n,
  }
  return data


async def main(
  request: Request | None = None,
  sequence: List[str] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.permutations = await get_permutations(sequence=data.body.sequence)
  data = await check_permutations_for_squares(data=data)
  data = await get_response(data=data)
  return data

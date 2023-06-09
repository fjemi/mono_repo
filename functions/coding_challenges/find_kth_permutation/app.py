#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Any
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  n: int = 0
  k: int = 0


@dc.dataclass
class Data:
  body: Body | None = None
  chars: List[str] | None = None
  permutations: List[str] | None = None
  output: str | None = None


GET_CHARS = {
  0: lambda chars, n: chars,
  1: lambda chars, n: [str(i + 1) for i in range(n)],
}


async def get_chars(chars: List[str], n: int) -> List[Any]:
  _case = chars is None
  function = GET_CHARS[_case]
  return function(chars=chars, n=n)


async def get_permutations(chars: List[str]) -> List[str]:
  chars_range = range(len(chars))
  permutations = [chars]

  count = len(chars) - 1
  while count > 0:
    previous_branches = permutations[-1]
    previous_branches_range = range(len(previous_branches))
    store = []
    for i in previous_branches_range:
      branch = previous_branches[i]
      for j in chars_range:
        char = chars[j]
        if branch.find(char) != -1:
          continue
        next_branch = f'{branch}.{char}'
        store.append(next_branch)
    permutations.append(store)
    count += -1
  return permutations[-1]


async def process_permutations(
  permutations: List[str],
  k: int,
) -> str:
  permutations.sort()
  k = k - 1
  permutations_n = len(permutations)
  if k >= permutations_n:
    return None
  output = permutations[k]
  output = output.replace('.', '')
  return output


async def get_response(data: Data) -> dict:
  return {'kth_permutation': data.output}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  n: int | None = None,
  k: int | None = None,
) -> Data:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.chars = await get_chars(chars=data.chars, n=data.body.n)
  data.permutations = await get_permutations(chars=data.chars)
  data.output = await process_permutations(
    permutations=data.permutations,
    k=data.body.k,
  )
  data = await get_response(data=data)
  return data

#!/usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import List, Any
import yaml

from api import models


@dataclass
class Body:
  n: int = 0
  k: int = 0


@dataclass
class RequestData:
  body: Body | None = None


@dataclass
class Request:
  data: RequestData | None = None


@dataclass
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


async def get_response(data: Data) -> models.Data:
  data.output = str(data.output)
  data = f'''
    input: {asdict(data.body)}
    output: 
      kth_permutation: {data.output}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> Data:
  data = Data(body=request.data.body)
  request = None
  data.chars = await get_chars(chars=data.chars, n=data.body.n)
  data.permutations = await get_permutations(chars=data.chars)
  data.output = await process_permutations(
    permutations=data.permutations,
    k=data.body.k,
  )
  data = await get_response(data=data)
  return data

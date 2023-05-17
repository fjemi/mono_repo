#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict
import yaml

from api import models


DIGIT_LETTER_MAPPING = {
  '2': ['A', 'B', 'C'],
  '3': ['D', 'E', 'F'],
  '4': ['G', 'H', 'I'],
  '5': ['J', 'K', 'L'],
  '6': ['M', 'N', 'O'],
  '7': ['P', 'Q', 'R', 'S'],
  '8': ['T', 'U', 'V'],
  '9': ['W', 'X', 'Y', 'Z'],
}


@dataclass
class Body(models.Body):
  digits: str | int = ''


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  combinations: List[str] = field(default_factory=lambda: [])
  digit_letter_mapping: Dict[int, List[str]] = field(default_factory=lambda: DIGIT_LETTER_MAPPING)


async def case_digits_length_greater_than_equal_one(
  digits: str,
  digit_letter_mapping: Dict[int, List[str]],
) -> List[str]:
  # Set the first letter of each string
  root = digits[0]
  roots = digit_letter_mapping[root]
  store = [roots]

  # Create combinations using current combination and char
  digits_n = len(digits)
  for i in range(1, digits_n):
    digit = digits[i]
    branch_store = []
    previous_branches = store[-1]
    # Combine previous branch with current letters
    # To form combinations of letters
    for previous_branch in previous_branches:
      chars = digit_letter_mapping[digit]
      for char in chars:
        current_branch = f'{previous_branch}{char}'
        branch_store.append(current_branch)
    store.append(branch_store)
  return store


async def case_digits_length_equals_zero(
  digits: str,
  digit_letter_mapping: Dict[int, List[str]],
) -> List[List]:
  _ = digits, digit_letter_mapping
  return [[]]


GET_COMBINATIONS = {
  0: case_digits_length_equals_zero,
  1: case_digits_length_greater_than_equal_one,
  2: case_digits_length_greater_than_equal_one,
}


async def get_combinations(
  digits: str,
  digit_letter_mapping: Dict[int, List[str]],
) -> List[str]:
  digits_n = len(digits)

  cases = [
    digits_n == 0,
    digits_n == 1,
    digits_n not in [0, 1],
  ]
  index = cases.index(1)
  function = GET_COMBINATIONS[index]
  result = await function(
    digits=digits,
    digit_letter_mapping=digit_letter_mapping,
  )
  return result


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: {data.combinations}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  # Pre-processing
  data = Data(body=request.data.body)
  request = None
  data.body.digits = str(data.body.digits)
  # Processing
  data.combinations = await get_combinations(
    digits=data.body.digits,
    digit_letter_mapping=data.digit_letter_mapping,
  )
  # Post-processing
  data.combinations = data.combinations[-1]
  data = await get_response(data=data)
  return data

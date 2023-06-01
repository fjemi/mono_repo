#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


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


@dc.dataclass
class Body:
  digits: str | int = ''


@dc.dataclass
class Data:
  body: Body | None = None
  combinations: List[str] = dc.field(default_factory=lambda: [])
  digit_letter_mapping: Dict[int, List[str]] = dc.field(
    default_factory=lambda: DIGIT_LETTER_MAPPING)


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


async def get_response(data: Data) -> dict:
  return {'combinations': data.combinations}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  digits: str | int | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
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

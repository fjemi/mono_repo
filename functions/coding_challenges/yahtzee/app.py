#!/usr/bin/env python3

from typing import List, Dict
import dataclasses as dc
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments

@dc.dataclass
class Body:
  dice_roll: List[int] | None = None


@dc.dataclass
class UpperSectionScores:
  dice: Dict[int, int] | None = None
  max_score: int = 0


@dc.dataclass
class Data:
  body: Body | None = None
  upper_section_scores: UpperSectionScores | None = None


async def count_dice(data: Data) -> Data:
  store = {}
  for dice in data.body.dice_roll:
    if dice not in store:
      store[dice] = 0
    store[dice] += 1
  data.upper_section_scores = UpperSectionScores(dice=store)
  return data


async def get_max_score(data: Data) -> Data:
  store = {}
  max_score = 0
  for key, value in data.upper_section_scores.dice.items():
    score = key * value
    store[key] = score
    if score > max_score:
      max_score = score
  data.upper_section_scores.dice = store
  data.upper_section_scores.max_score = max_score
  return data


async def get_response(data: Data) -> dict:
  data = {
    'dice': list(data.upper_section_scores.dice.keys()),
    'scores': list(data.upper_section_scores.dice.values()),
    'max_score': data.upper_section_scores.max_score,
  }
  return data


# pylint: disable=unused-argument
async def main(
  request: Request,
  dice_roll: List[int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await count_dice(data=data)
  # data = await get_upper_section_scores(data=data)
  data = await get_max_score(data=data)
  data = await get_response(data=data)
  return data



from typing import List, Dict
from dataclasses import dataclass, field, asdict
import yaml

from api import models


@dataclass
class Body(models.Body):
  dice_roll: List[int] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class UpperSectionScores:
  dice: Dict[int, int] | None = None
  max_score: int = 0


@dataclass
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


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      upper_section_scores: {asdict(data.upper_section_scores)}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data = await count_dice(data=data)
  # data = await get_upper_section_scores(data=data)
  data = await get_max_score(data=data)
  data = await get_response(data=data)
  return data

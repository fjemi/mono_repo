#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List, Dict
import yaml

from api import models 


@dataclass
class Body:
  scores: List[int] | None = None
  ages: List[int] | None = None
  

@dataclass
class Data:
  body: Body | None = None


@dataclass
class Request:
  data: Data | None = None


@dataclass
class Data:
  body: Body | None = None
  total_score: int = 0


async def get_scores_by_ages(
  scores: List[int],
  ages: List[int],
) -> Dict[int, List[Dict]]:
  store = {}
  scores_n = range(len(scores))
  for i in scores_n:
    age = ages[i]
    if age not in store:
      store[age] = []
    store[age].append(scores[i])
  return store


async def get_succeeding_scores(
  i: int,
  ages: List[int],
  scores_by_ages: Dict[int, List[int]],
) -> List[int]:
  store = []
  ages_slice = ages[i + 1:]
  for age in ages_slice:
    store.extend(scores_by_ages[age])
  return store


async def get_non_conflicting_scores(
  scores: List[int],
  non_conflicting_scores: List[int],
  succeeding_scores: List[int],
) -> List[int]:
  scores.sort(reverse=True)
  scores_n = range(len(scores))
  succeeding_scores_n = range(len(succeeding_scores))
  conflicting = [False for i in scores_n]

  for i in scores_n:
    for j in succeeding_scores_n:
      if scores[i] <= succeeding_scores[j]:
        continue
      conflicting[i] = True
      break

  conflicting_n = range(len(conflicting))
  pointer = len(conflicting)
  for i in conflicting_n:
    if i > pointer:
      break

    if conflicting[i] is False:
      non_conflicting_scores.append(scores[i])
      continue

    conflicting_slice = conflicting[i + 1:pointer]
    conflicting_slice_n = len(conflicting_slice)

    if conflicting_slice_n < 1:
      continue
    non_conflicting_scores.append(scores[i])
    conflicting[pointer - 1] = True
    pointer += -1

  return non_conflicting_scores


async def get_total_score(scores_by_ages: Dict[int, int]) -> int:
  ages = list(scores_by_ages.keys())
  ages.sort()

  non_conflicting_scores = []
  ages_n = range(len(ages) - 1)
  for i in ages_n:
    age = ages[i]
    scores = scores_by_ages[age]
    succeeding_scores = await get_succeeding_scores(
      i=i,
      ages=ages,
      scores_by_ages=scores_by_ages,
    )
    non_conflicting_scores = await get_non_conflicting_scores(
      succeeding_scores=succeeding_scores,
      scores=scores,
      non_conflicting_scores=non_conflicting_scores,
    )

  non_conflicting_scores.extend(scores_by_ages[ages[-1]])
  total_score = sum(non_conflicting_scores)
  return total_score


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      total_score: {data.total_score}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  scores_by_ages = await get_scores_by_ages(
    scores=data.body.scores,
    ages=data.body.ages,
  )
  data.total_score = await get_total_score(
    scores_by_ages=scores_by_ages)
  data = await get_response(data=data)
  return data

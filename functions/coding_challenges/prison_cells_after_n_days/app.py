#!/usr/bin/env python3


from dataclasses import dataclass, asdict
from typing import List
from copy import deepcopy
import yaml

from api import models


@dataclass 
class Body(models.Body):
  k: int = 0
  head: List[int] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  states: List[List[int]] | None = None


async def pre_processing(data: Data) -> Data:
  data.states = [data.body.cells]
  return data


async def get_states(states: List[List[int]], n: int) -> List[List[int]]:
  for i in range(n):
    previous_state = states[i]
    next_state = deepcopy(states[i])
    state_n = len(next_state)
    for j in range(state_n):
      # Cells at the ends of the row
      if j in [0, state_n - 1]:
        next_state[0] = 0
        next_state[7] = 0
        continue

      # If adjacent cells are equal, the cell becomes occupied
      cell_a = previous_state[j - 1]
      cell_c = previous_state[j + 1]
      if cell_a == cell_c:
        next_state[j] = 1
        continue
      # If adjacent cells are not equal, the cell becomes vacant
      if cell_a != cell_c:
        next_state[j] = 0
    states.append(next_state)
  return states


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: {data.states[-1]}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data = await pre_processing(data=data)
  data.states = await get_states(states=data.states, n=data.body.n)
  data = await get_response(data=data)
  return data

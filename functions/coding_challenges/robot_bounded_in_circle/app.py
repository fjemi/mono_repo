#!/usr/bin/env python3

from typing import List, Dict
from dataclasses import dataclass, field, asdict
import yaml

from api import models


DIRECTION_MAP = {
  'north': [0, 1],
  'east': [1, 0],
  'south': [0, -1],
  'west': [-1, 0],
}


TURN_MAP = {
  'R': 1,
  'L': -1,
}


@dataclass
class Body(models.Body):
  instructions: str = ''
  repeat_limit: int = 10


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class State:
  position: List[int] | None = None
  facing: List[str] | None = None
  repeats: int = 0
  bound_in_circle: bool = False


@dataclass
class Data:
  body: Body | None = None
  state: State | None = None
  direction_map: Dict[str, List[int]] = field(
    default_factory=lambda: DIRECTION_MAP)
  turn_map: Dict[str, List[int]] = field(
    default_factory=lambda: TURN_MAP)


async def get_initial_state() -> State:
  position = [[0, 0]]
  facing = ['north']
  state = State(position=position, facing=facing)
  return state


async def go_straight_one_unit(
  data: Data,
  instruction: None = None,
) -> Data:
  _ = instruction
  facing = data.state.facing[-1]
  i, j = data.direction_map[facing]
  data.state.facing.append(facing)

  a, b = data.state.position[-1]
  position = [a + i, b + j]
  data.state.position.append(position)
  return data


async def turn_facing_direction(
  data: Data,
  instruction: str,
) -> Data:
  position = data.state.position[-1]
  data.state.position.append(position)
  facing = data.state.facing[-1]

  directions = list(data.direction_map.keys())
  current_i = directions.index(facing)
  increment = data.turn_map[instruction]
  next_i = current_i + increment

  n = len(directions) - 1
  if next_i < 0:
    next_i = n
  if next_i > n:
    next_i = 0

  next_facing = directions[next_i]
  data.state.facing.append(next_facing)
  return data


INSTRUCTION_SWITCHER = {
  'G': go_straight_one_unit,
  'L': turn_facing_direction,
  'R': turn_facing_direction,
}


async def perform_instructions(data: Data) -> Data:
  while data.state.repeats < data.body.repeat_limit:
    for instruction in data.body.instructions:
      switcher = INSTRUCTION_SWITCHER[instruction]
      data = await switcher(
        data=data,
        instruction=instruction,
      )
    if data.state.position.count([0, 0]) > 1:
      data.state.bound_in_circle = True
      break
    data.state.repeats += 1
  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      states: {asdict(data.state)}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  body = Body(**asdict(request.data.body))
  data = Data(body=body)
  request = None
  data.state = await get_initial_state()
  data = await perform_instructions(data=data)
  data = await get_response(data=data)
  return data

#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List, Dict
import yaml

from api import models


@dataclass
class Body(models.Body):
  grid: List[List[int]] = field(default_factory=lambda: [])


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  states: Dict[str, List[int]] = field(default_factory=lambda: {})
  adjacent_positions: Dict[str, List[str]] = field(default_factory=lambda: {})
  minutes: int = 0
  fresh_oranges: List[str] | None = None


async def get_adjacent_positions(
  i: int,
  j: int,
  grid_m: int,
  grid_n: int,
) -> List[str]:
  # Increments to step to adjacent positios
  steps = [
    [1, 0],
    [-1, 0],
    [0, 1],
    [0, -1],
  ]

  store = []
  for step in steps:
    # Step to adjacent position
    position_i = i + step[0]
    position_j = j + step[1]
    # Conditions for ignoring the adajacent position
    conditions = [
      position_i < 0,
      position_j < 0,
      [position_i, position_j] == [i, j],
      position_i >= grid_m,
      position_j >= grid_n,
    ]
    if True in conditions:
      continue

    position = f'{position_i}.{position_j}'
    store.append(position)
  return store


async def get_position_states_and_adjacent_positions(data: Data) -> Data:
  # Grid dimensions
  grid_m = len(data.body.grid)
  grid_n = len(data.body.grid[0])

  # Set initial state for each position in the grid
  for i in range(grid_m):
    for j in range(grid_n):
      state = data.body.grid[i][j]
      position = f'{i}.{j}'
      data.states[position] = [state]
      data.adjacent_positions[position] = await get_adjacent_positions(
        i=i,
        j=j,
        grid_m=grid_m,
        grid_n=grid_n,
      )
  return data


async def case_previous_state_is_zero_or_two(
  adjacent_positions: List[str],
  states: Dict[str, List[int]],
  position: str,
) -> Dict[str, List[int]]:
  _ = adjacent_positions

  # Set current state as previous state
  previous_state = states[position][-1]
  states[position].append(previous_state)
  return states


async def case_previous_state_is_one(
  adjacent_positions: List[str],
  states: Dict[str, List[int]],
  position: str,
) -> Dict[str, List[int]]:
  states_i = len(states[position]) - 1
  adjacent_states = []
  for adjacent_position in adjacent_positions:
    state = states[adjacent_position][states_i]
    adjacent_states.append(state)

  current_state = 1
  if adjacent_states.count(2) > 0:
    current_state = 2

  states[position].append(current_state)
  return states


NEXT_STATES = {
  0: case_previous_state_is_zero_or_two,
  1: case_previous_state_is_one,
  2: case_previous_state_is_zero_or_two,
}


async def process_data(data: Data) -> Data:
  # Flag for exiting while loop
  _continue = True

  # Each iteration represents a minute in time, which is the time
  # to determine if any fresh oranges have rotted
  while _continue:
    changed = []
    fresh_oranges = []

    # Check state of positions in the grid
    for position in data.states:
      previous_state = data.states[position][-1]
      function = NEXT_STATES[previous_state]
      data.states = await function(
        states=data.states,
        adjacent_positions=data.adjacent_positions[position],
        position=position,
      )

      states = data.states[position]
      # An orange rottened if previous and current states are different
      if states[-2] != states[-1]:
        changed.append(position)
      # Store position of fresh oranges
      if states[-1] == 1:
        fresh_oranges.append(position)

    data.fresh_oranges = fresh_oranges
    data.minutes += 1

    # Exit loop if no changes during this iteration
    if len(changed) == 0:
      data.minutes += -1
      _continue = False

  return data


async def post_processing(data: Data) -> Data:
  # No processing needed. All fresh oranges have rotted
  fresh_oranges_n = len(data.fresh_oranges)
  if fresh_oranges_n == 0:
    return data
  # No solution. Fresh oranges remain on the grid
  data.minutes = -1
  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      minutes: {data.minutes}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  data = await get_position_states_and_adjacent_positions(data=data)
  data = await process_data(data=data)
  data = await post_processing(data=data)
  data = await get_response(data=data)
  return data

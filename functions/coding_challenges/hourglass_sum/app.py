#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List
import yaml

from api import models


# Counts to exclude in for loop
EXCLUDE_COUNTS = [3, 5]


@dataclass
class Body(models.Body):
  array: List[List[int]] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Hourglass:
  positions: List = field(default_factory=lambda: [])
  values: List = field(default_factory=lambda: [])
  total: int = 0


@dataclass
class Data:
  body: Body | None = None
  start_positions: List = field(default_factory=lambda: [])
  hourglasses: List[Hourglass] = field(default_factory=lambda: [])
  max_hourglass_total: int = 0


async def get_hourglasses_positions_and_values(data: Data) -> List:
  '''Returns the position and value of cells that make up an hourglass, and 
  keeps tracks of the hourglass with the max value'''
  store = []
  for start in data.start_positions:
    hourglass = Hourglass()
    count = -1
    for i in range(3):
      for j in range(3):
        count = count + 1
        # Third and fith counts do not fall in hour glass
        if count in EXCLUDE_COUNTS:
          continue
        # Set the position from the start
        position_i = start[0] + i
        position_j = start[1] + j
        # Store position, value, and total values
        value = data.body.array[position_i][position_j]
        hourglass.positions.append([position_i, position_j])
        hourglass.values.append(value)
        hourglass.total += value
      store.append(hourglass)
      # Keep track of the max valued hourglass
      if hourglass.total > data.max_hourglass_total:
        data.max_hourglass_total = hourglass.total
  data.hourglasses = store
  return data


async def get_start_positions(data: Data) -> List[List]:
  '''Returns the starting positions of hour glasses within an array'''
  store = []

  m = len(data.body.array)
  n = len(data.body.array[0])
  # Handle array with length/width less than 3
  if m < 3 or n < 3:
    return store
  # Handle all other cases
  for i in range(m - 2):
    for j in range(n - 2):
      # Exit loop if j will exceed row length
      if j + 2 > len(data.body.array[0]):
        break
      position = [i, j]
      store.append(position)
    # Exit loop if i will exceed column length
    if i + 2 > len(data.body.array):
      break
  return store


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      hourglasses_sum: {data.max_hourglass_total}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data.start_positions = await get_start_positions(data=data)
  data = await get_hourglasses_positions_and_values(data=data)
  data = await get_response(data=data)
  return data

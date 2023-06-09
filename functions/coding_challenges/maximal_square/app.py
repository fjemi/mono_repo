#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from math import sqrt
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  matrix: List[List[int]] = dc.field(default_factory=lambda: [])


@dc.dataclass
class Data:
  body: Body | None = None
  positions: Dict[str, int] = dc.field(default_factory=lambda: {})
  squares: Dict[str, List[List[str]]] = dc.field(default_factory=lambda: {})
  maximal_squares: Dict[int, List[List[str]]] = dc.field(default_factory=lambda: {})


async def get_steps(
  position: List[int],
  max_dimension: int,
  matrix_m: int,
  matrix_n: int,
) -> List[int]:
  i, j = position

  store = []
  for x in range(max_dimension):
    a = i + x
    b = j + x

    conditions = [
      a >= matrix_m,
      b >= matrix_n,
    ]
    if True in conditions:
      continue
    # Steps should start at 1 instead of 0 for correct number of iterations
    store.append(x + 1)
  return store


async def get_squares_for_position(
  position: List[int],
  steps: List[int],
  matrix_m: int,
  matrix_n: int,
) -> List[List[str]]:
  squares = []
  for step in steps:
    store = []
    for a in range(step):
      for b in range(step):
        conditions = [
          position[0] + a >= matrix_m,
          position[1] + b >= matrix_n,
        ]
        if True in conditions:
          store = []
          break
        square_position = f'{position[0] + a}.{position[1] + b}'
        store.append(square_position)
    if len(store) == 0:
      continue
    squares.append(store)
  return squares


async def pre_processing(data: Data) -> Data:
  squares = {}

  matrix_m = len(data.body.matrix)
  matrix_n = len(data.body.matrix[0])
  max_dimension = max(matrix_n, matrix_m)

  for i in range(matrix_m):
    for j in range(matrix_n):
      position = f'{i}.{j}'
      data.positions[position] = data.body.matrix[i][j]
      data.squares[position] = []
      steps = await get_steps(
        matrix_m=matrix_m,
        matrix_n=matrix_n,
        max_dimension=max_dimension,
        position=[i, j]
      )
      squares = await get_squares_for_position(
        position=[i, j],
        steps=steps,
        matrix_m=matrix_m,
        matrix_n=matrix_n,
      )
      data.squares[position] = squares
  return data


async def process_squares(
  squares: Dict[str, List[str]],
  positions: Dict[str, int],
) -> Data:
  store = {}
  for position_squares in squares.values():
    for square in position_squares:
      if square == []:
        continue
      square_values = []
      for square_position in square:
        value = positions[square_position]
        if value == 0:
          square_values = []
          break
        square_values.append(value)
      square_n = len(square_values)

      # Ignore conditions
      conditions = [
        # square_n == 0,
        square_n != sum(square_values),
      ]
      if True in conditions:
        continue

      # Store square with its area as a key
      key = sqrt(square_n) ** 2
      if key not in store:
        store[key] = []
      store[key].append(square)
  return store


async def get_maximal_squares(squares):
  max_area = max(squares)
  return {max_area: squares[max_area]}


async def get_response(data: Data) -> dict:
  data = {
    'count': list(data.maximal_squares.keys())[0],
    'largest_squares': list(data.maximal_squares.values()),
  }
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  matrix: List[List[int]] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await pre_processing(data=data)
  data.squares = await process_squares(squares=data.squares, positions=data.positions)
  data.maximal_squares = await get_maximal_squares(squares=data.squares)
  data = await get_response(data=data)
  return data

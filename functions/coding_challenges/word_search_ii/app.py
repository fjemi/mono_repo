#!/usr/bin/env python3

from __future__ import annotations
import dataclasses as dc
from typing import List, Dict
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  board: List[List[str]] | None = None
  words: List[str] | Dict[int, List[str]] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  values: Dict[str, str] = dc.field(default_factory=lambda: {})
  adjacent_positions: Dict[str, List[str]] = dc.field(
    default_factory=lambda: {})
  positions: Dict[str, str] = dc.field(default_factory=lambda: {})


async def get_adjacent_positions(
  position: List[str],
  upper_bounds: List[str],
) -> List[str]:
  store = []
  steps = [
    [0, 1],
    [1, 0],
    [0, -1],
    [-1, 0],
  ]
  i, j = position
  for step in steps:
    a = i + step[0]
    b = j + step[1]

    ignore_conditions = [
      a < 0,
      b < 0,
      a >= upper_bounds[0],
      b >= upper_bounds[1],
      [a, b] == [i, j],
    ]
    if True in ignore_conditions:
      continue

    position = f'{a}.{b}'
    store.append(position)
  return store


async def get_positions_values_and_adjacent_positions(data: Data) -> Data:
  board_m = len(data.body.board)
  board_n = len(data.body.board[0])

  for i in range(board_m):
    for j in range(board_n):
      position = f'{i}.{j}'
      value = data.body.board[i][j]
      data.positions[position] = data.body.board[i][j]
      data.adjacent_positions[position] = await get_adjacent_positions(
        position=[i, j],
        upper_bounds=[board_m, board_n]
      )
      if value not in data.values:
        data.values[value] = []
      data.values[value].append(position)

  return data


async def find_word_on_board(word: str, data: Data) -> List[str]:
  char = word[0]
  # Return empty list if first char in word not on board
  if char not in data.values:
    return []

  tree = [data.values[char]]
  exit_loop = False
  char_i = 1
  word_n = len(word) - 1

  # Find the word by creating branches of
  # underscore delimited position strings
  while exit_loop is False and char_i <= word_n:
    previous_branches = tree[-1]
    store = []
    for branch in previous_branches:
      branch_leaf = branch.split('_')[-1]
      adjacent_positions = data.adjacent_positions[branch_leaf]
      for position in adjacent_positions:
        # Ignore positions already visited
        if branch.find(position) != -1:
          continue
        leaf = data.positions[position]
        # Ignore positions with non-matching chars
        if leaf != word[char_i]:
          continue
        next_branch = f'{branch}_{position}'
        store.append(next_branch)
    # Empty list means word can't be found; exit the while loop.
    if len(store) == 0:
      exit_loop = True
    tree.append(store)
    char_i += 1
  # Returns the branches that form or word,
  # or the empty list if the formation isn't possible
  return tree[-1]


async def find_word_positions(data: Data) -> Data:
  store = {}
  for word in data.body.words:
    positions = await find_word_on_board(word=word, data=data)
    # Split string positions into list of positions
    positions_n = len(positions)
    for i in range(positions_n):
      positions[i] = positions[i].split('_')
    store[word] = positions
  return store


async def get_response(data: Data) -> dict:
  # words = list(data.body.words.keys())
  return {'words': data.body.words}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  board: List[List[str]] | None = None,
  words: List[str] | Dict[int, List[str]] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await get_positions_values_and_adjacent_positions(data=data)
  data.body.words = await find_word_positions(data=data)
  data = await get_response(data=data)
  return data

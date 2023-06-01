#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict, Any
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


# Step to horizontal and vertical neighbors
NEIGHBOR_STEPS = [
  [1, 0],
  [-1, 0],
  [0, 1],
  [0, -1],
]


@dc.dataclass
class Shape:
  board_m: int = 0
  board_n: int = 0


@dc.dataclass
class Positions:
  chars: Dict | None = None
  neighbors: Dict | None = None


@dc.dataclass
class Body:
  board: List[List[Any]] | None = None
  word: str = ''


@dc.dataclass
class Data:
  body: Body | None = None
  shape: dict | Shape | None = None
  positions: Positions | None = None
  neighbor_steps: List[List[int]] = dc.field(
    default_factory=lambda: NEIGHBOR_STEPS)
  paths: List[List[str]] | None = None


async def get_positions_for_chars(
  i: int,
  j: int,
  chars: Dict[str, List[str]],
  char: str,
) -> Dict[str, List[str]]:
  if char not in chars:
    chars[char] = []
  position = f'{i}.{j}'
  chars[char].append(position)
  return chars


# pylint: disable=too-many-arguments
async def get_positions_for_neighbors(
  shape: Shape,
  i: int,
  j: int,
  neighbors: Dict,
  neighbor_steps: List[List[int]],
  board: List[List[str]],
  word: str,
) -> Dict[str, List[str]]:
  position = f'{i}.{j}'
  neighbors[position] = []
  for step in neighbor_steps:
    a, b = step
    a = a + i
    b = b + j

    conditions = [
      a < 0,
      b < 0,
      a >= shape.board_m,
      b >= shape.board_n,
    ]
    if True in conditions:
      continue

    neighbor_char = board[a][b]
    if word.find(neighbor_char) == -1:
      continue

    neighbor = f'{a}.{b}'
    neighbors[position].append(neighbor)
  return neighbors


async def get_positions(
  board: List[List[Any]],
  shape: Shape,
  neighbor_steps: List[List[int]],
  word: str,
) -> Positions:
  chars = {}
  neighbors = {}

  for i in range(shape.board_m):
    for j in range(shape.board_n):
      char = board[i][j]
      if word.find(char) == -1:
        continue

      chars = await get_positions_for_chars(
        i=i,
        j=j,
        chars=chars,
        char=char,
      )
      neighbors = await get_positions_for_neighbors(
        shape=shape,
        i=i,
        j=j,
        neighbors=neighbors,
        neighbor_steps=neighbor_steps,
        board=board,
        word=word,
      )

  positions = Positions(
    chars=chars,
    neighbors=neighbors,
  )
  return positions


async def pre_processing(data: Data) -> Data:
  data.shape = Shape(
    board_m=len(data.body.board),
    board_n=len(data.body.board[0]),
  )
  data.positions = await get_positions(
    board=data.body.board,
    shape=data.shape,
    neighbor_steps=data.neighbor_steps,
    word=data.body.word,
  )
  return data


async def get_tree_roots(
  chars: Dict[str, List[str]],
  word: str,
) -> List[str]:
  char = word[0]
  if char not in chars:
    return []
  return chars[char]


async def get_tree_branches(
  tree_roots: Dict[int, List[str]],
  positions: Positions,
  word: str,
) -> Dict[int, List[str]]:
  tree = {0: tree_roots}

  for i in range(1, len(word)):
    store = []
    char = word[i]
    if char not in positions.chars:
      break

    index = i - 1
    if index not in tree:
      break

    branches = tree[index]
    for branch in branches:
      leaf = branch.split('|')[-1]
      neighbors =  positions.neighbors[leaf]

      for neighbor in neighbors:
        if neighbor not in positions.chars[char]:
          continue
        next_branch = f'{branch}|{neighbor}'
        store.append(next_branch)

    tree[i] = store
  return tree


async def get_paths_from_tree_branches(
  word: str,
  tree_branches: Dict[int, List[str]],
) -> List[str]:
  index = len(word) - 1
  if index not in tree_branches:
    return []
  return tree_branches[index]


async def get_paths(
  positions: Positions,
  word: str,
) -> List[str]:
  tree_roots = await get_tree_roots(
    chars=positions.chars,
    word=word,
  )
  tree_branches = await get_tree_branches(
    positions=positions,
    word=word,
    tree_roots=tree_roots,
  )
  paths = await get_paths_from_tree_branches(
    tree_branches=tree_branches,
    word=word,
  )
  return paths


async def get_response(data: Data) -> dict:
  return {'paths': data.paths}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  board: List[List[Any]] | None = None,
  word: str = '',
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await pre_processing(data=data)
  data.paths = await get_paths(positions=data.positions, word=data.body.word)
  data = await get_response(data=data)
  return data

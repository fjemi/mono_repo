#!/usr/bin/env python3

import numpy as np
import random
from dataclasses import dataclass, field
from typing import List, Dict
from random import randint

from api import models as api_models


@dataclass
class Shape:
  m: int = 0
  n: int = 0


@dataclass
class Data:
  shape: Shape | None = None
  n: int = 0
  m: int = 0
  adjacent_positions: Dict[str, List] = field(default_factory=lambda: {})
  mines: List[int] = field(default_factory=lambda: [])
  scores: Dict[str, int] = field(default_factory=lambda: {})
  moves: List[List[int]] = field(default_factory=lambda: [])
  player_score: List[int] = field(default_factory=lambda: [])
  mine_hit: bool = False


def get_mine_positions(data: Data) -> List:
  '''
  # Description
  Creates mines at random positions on the board
  '''
  mines = []
  # Bound the number of mines created
  squares = data.m  * data.n
  mine_count_lower_bound = int(squares * .25)
  mine_count_upper_bound = int(squares * .75)
  mine_count = randint(mine_count_lower_bound, mine_count_upper_bound)
  # Get random mine positions
  for count in range(mine_count):
    i = randint(0, data.m)
    j = randint(0, data.n)
    mines.append([i, j])
  return mines


def get_adjacent_positions(
  width_upper_bound: int, 
  length_upper_bound: int, 
  position: List[int],
) -> List[List[int]]:
  '''
  Description
  Returns the positions of squares adjacent to a specified square
  '''
  adjacent_positions = []
  # Get adjadent positions
  for k in range(position[0] - 1, position[0] + 2):
    for l in range(position[1] - 1, position[1] + 2):
      # Conditions for a position to be inside the board
      conditions = [
        k >= 0,
        l >= 0,
        k <= width_upper_bound,
        l <= length_upper_bound,
        [k, l] != position,
      ]
      # Handle positions outside the bounds
      if sum(conditions) < len(conditions):
        continue
      adjacent_positions.append([k, l])

  return adjacent_positions


def get_position_scores(data: Data) -> Dict[str, int]:
  '''
  # Description
  Returns the score or total number of adjacent positions that are mines, for 
  the squares on the board
  '''
  scores = {}

  for i in range(data.m):
    for j in range(data.n):
      key = f'{i}_{j}'
      position = [i, j]
      adjacent_positions = get_adjacent_positions(
        width_upper_bound=data.m, 
        length_upper_bound=data.n, 
        position=position,
      )
      data.adjacent_positions[key] = adjacent_positions
      score = 0
      for position in adjacent_positions:
        if position in data.mines:
          score += 1
      scores[key] = score
  return scores


def access_a_move(data: Data, move: List[int]) -> Data:
  '''
  # Description
  Accesses the outcome of a move. If the move lands on a mine the game is over 
  and the player's score is zero. If it lands on a blank, add the score for the 
  square to the players score and unveal adjacent squares.
  '''
  data.moves.append(move)
  
  # Handle moving onto a mine
  if move in data.mines:
    data.player_score = []
    data.mine_hit = True
    return data
  # Handle moving onto a blank
  key = f'{move[0]}_{move[1]}'
  position_score = data.scores[key]
  data.player_score.append(position_score)
  # Reveal squares
  
  return data


data = Data(n=4, m=4)
print(data)
data.mines = get_mine_positions(data=data)
print(data)
data.scores = get_position_scores(data=data)
print(data)
data = access_a_move(data=data, move=[1,1])
print(data)
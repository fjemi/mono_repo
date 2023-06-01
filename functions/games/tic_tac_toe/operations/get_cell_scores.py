from dataclasses import dataclass
from typing import List, Union


@dataclass
class Game:
  n: int = 0
  # board
  # possible_wins
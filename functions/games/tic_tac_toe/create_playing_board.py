from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Game:
  n: int = 1  
  board: Dict[str, str] = field(default_factory=lambda: {'00': ''})


def create_playing_board(game: Union[Game, dict]) -> Game:
  '''Creates an nxn board to play on'''
  if isinstance(game, dict):
    game = Game(**game)

  board = {}
  # Add cells to the board. 
  for i in range(game.n):
    for j in range(game.n):
      # Cell cooridates 'ij' represent 
      # the keys of the dictionary
      square = f'{i}{j}'
      board[square] = ''
  game.board = board
  return game




# if __name__ == '__main__':

#   game = {'n': 0}
#   game = create_playing_board(game=game)
#   # Grid should have 0 cells in the board
#   assert game.board == {}

#   game = {'n': 1}
#   game = create_playing_board(game=game)
#   # Grid should have 1 cells in the board
#   assert game.board == {'00': ''}

#   game = Game(n=2)
#   game = create_playing_board(game=game)
#   # Should have 4 cells in the board
#   assert game.board == {'00': '', '01': '', '10': '', '11': ''}

from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class Cell:
  i: int = 0
  j: int = 0


@dataclass
class Win:
  direction: str = None
  cells: List[Cell] = None


@dataclass
class Increment:
  direction: str = None
  i: int = 0
  j: int = 0


def increment_cell(cell: Cell, increment: Increment) -> Cell:
  ''''''
  cell.i += increment.i
  cell.j += increment.j
  return cell


ADDERS = [
  Increment(direction='horizontal_left', i=-1, j=0),
  Increment(direction='horizontal_right', i=1, j=0),
  Increment(direction='vertical_up', i=0, j=1),
  Increment(direction='vertical_down', i=0, j=-1),
  Increment(direction='diagonal_right_down', i=1, j=-1),
  Increment(direction='diagonal_right_up', i=1, j=1),
  Increment(direction='diagonal_left_down', i=-1, j=-1),
  Increment(direction='diagonal_left_up', i=-1, j=1), ]


@dataclass
class Move:
  player: str = ''
  position: Cell = None


@dataclass
class Game:
  board: List[Cell] = field(default_factory=lambda: [])
  board_dict: dict = field(default_factory=lambda: {})
  n: int = 0
  possible_wins: List[Win] = None
  possible_wins_dict: dict = None
  possible_wins_by_cell: dict = None
  cell_scores: dict = None
  moves: List[Move] = None


def get_cells_in_a_win(
  n: int = 0,
  cell: str = '00',
  adder: Increment = Increment(direction='', i=0, j=0),
) -> Win:
  '''
  Creates a list of cells that make up a win. 
  Parameters
    n: Size of nxn board
    start_cell: Cell at coordinates i,j to start from
    adder: Increment i,j of a cell
  Returns
    A list of cells that make up a win or None if cells are not on the board
  '''
  store = []

  i = int(cell[0])
  j = int(cell[1])

  for k in range(n):
    # Increment coordinates of starting cell 
    i_adjusted = i + adder.i * k
    j_adjusted = j + adder.j * k
    
    # Check that the coordinates fall within the board
    checks = [
      i_adjusted >= 0,
      j_adjusted >= 0,
      i_adjusted < n,
      j_adjusted < n, ]
    # Handle failed checks
    if False in checks:
      return None

    # Store incremented cell
    store.append(f'{i_adjusted}{j_adjusted}')
  store.sort()
  return Win(direction=adder.direction, cells=store)


def get_possible_wins(game: Union[Game, dict]) -> Game:
  '''
  Summary
    Get a list of possible wins for each cell and adder type
  Paramters
    game:
      - possible_wins: Store lists of cells that make up possible wins
      - n: Dimension for a nxn board
  '''

  if isinstance(game, dict):
    game = Game(**game)

  # game.possible_wins = []
  game.possible_wins_dict = {}

  for cell in game.board_dict:
    for adder in ADDERS:
      cells_in_a_win = get_cells_in_a_win(
        n=game.n,
        cell=cell,
        adder=adder, )
      if cells_in_a_win is None:
        continue
      
      cells_string = '_'.join(cells_in_a_win.cells)
      # Filter out duplicates
      if cells_string not in game.possible_wins_dict.keys():
        game.possible_wins_dict[cells_string] = cells_in_a_win.direction
      
      # game.possible_wins.append(cells_in_a_win)
  return game


def get_possible_wins_by_cell(game: Union[Game, dict]) -> Game:
  ''''''
  store = {}
  possible_wins = list(game.possible_wins_dict.keys())
  for cell in game.board_dict:
    store[cell] = []
    for possible_win in possible_wins:
      if cell in possible_win:
        store[cell].append(possible_win)
  game.possible_wins_by_cell = store
  return game


def score_cells(game: Union[Game, dict]) -> Game:
  ''''''
  total_possible_wins = 0

  for board_cell in game.board_dict:
    board_cell_state = game.board_dict[board_cell]
    # Skips cells that have been filled
    if board_cell_state != '':
      continue

    #
    possible_wins = game.possible_wins_by_cell[board_cell]
    total_possible_wins += len(possible_wins)
    for possible_win in possible_wins:
      cells = possible_win.split('_')
      cell_states = {}
      counter = {'': 0, 'x': 0, 'o': 0}
      
      for cell in cells:
        state = game.board_dict[cell]
        cell_states[cell] = state
        counter[state] += 1

      score = dict(viable=True)
      # Possible wins with mixed states aren't viable
      if counter['x'] > 0 and counter['o'] > 0:
        score = dict(viable=False)
      score['open_cells'] = counter[''] / game.n
    
      print(cell_states)
      print(dict(
        cell=cell, 
        possible_wins_count=len(possible_wins), 
        counter=counter,
        score=score))

  return game


if __name__ == '__main__':
  from dataclasses import asdict
  import json
  from pprint import pprint

  cells_in_a_win = get_cells_in_a_win(
    n=2, 
    cell='00', 
    adder=Increment('horizontal_right', 1, 0), )
  # assert cells_in_a_win == Win(direction='horizontal_right', cells=['Cell(i=0, j=0)', Cell(i=1, j=0)])
  # print(cells_in_a_win)

  cells_in_a_win = get_cells_in_a_win(
    n=2,
    cell='11',
    adder=Increment('diagonal_left_up', -1, -1), )
  # assert cells_in_a_win == Win(direction='diagonal_left_up', cells=[Cell(i=1, j=1), Cell(i=0, j=0)])
  # print(cells_in_a_win)

  game = {'n': 1, 'board_dict': {'00': ''}}
  game = get_possible_wins(game)
  game = get_possible_wins_by_cell(game)
  # pprint(asdict(game))
  # assert game.possible_wins == [
  #   Win(direction='horizontal_left', cells=[Cell(i=0, j=0)]), ]

  game = {'n': 0, 'board': [], 'board_dict': {}}
  game = get_possible_wins(game)
  # assert game.possible_wins == []

  game = {
    'n': 2,
    'board_dict': {'00': '', '01': '', '10': '', '11': ''}, }
  game = get_possible_wins(game)
  # assert game.possible_wins == [
  #   Win(direction='horizontal_right', cells=[Cell(i=0, j=0), Cell(i=1, j=0)]), 
  #   Win(direction='diagonal_right_up', cells=[Cell(i=0, j=0), Cell(i=1, j=1)]), 
  #   Win(direction='horizontal_left', cells=[Cell(i=1, j=0), Cell(i=0, j=0)]), 
  #   Win(direction='horizontal_right', cells=[Cell(i=0, j=1), Cell(i=1, j=1)]), 
  #   Win(direction='diagonal_right_down', cells=[Cell(i=0, j=1), Cell(i=1, j=0)]), 
  #   Win(direction='horizontal_left', cells=[Cell(i=1, j=1), Cell(i=0, j=1)]), 
  #   Win(direction='diagonal_left_up', cells=[Cell(i=1, j=1), Cell(i=0, j=0)]), ]
  game = get_possible_wins_by_cell(game)
  # pprint(asdict(game))

  game = {
    'n': 3, 
    'board_dict': {
      '00': 'x', '10': 'x', '20': '',
      '01': 'x', '11': 'o', '21': 'o',
      '02': '', '12': '', '22': ''}, }
  game = get_possible_wins(game)
  game = get_possible_wins_by_cell(game)
  game = score_cells(game)
  # print(json.dumps(asdict(game), indent=2))
  # pprint(asdict(game))
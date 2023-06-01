from box import Box
from dataclasses import dataclass, field, fields, asdict
from typing import List, Any
from random import randint


@dataclass
class Cell_Stats:
  state: str = ''
  count: int = None
  percent: float = None
  cells: List[str] = field(default_factory=list)


@dataclass
class Grid_Stats:
  available: List[Cell_Stats]
  x: List[Cell_Stats]
  o: List[Cell_Stats]


@dataclass
class Data:
  n: int = 3
  board: Union[list, dict] = None
  turn_order: List[str] = field(default_factory=list)
  turn_taken: List[Any]  = field(default_factory=list)
  cell_stats: List[List[Cell_Stats]] = field(default_factory=list)
  possible_wins: List[Any] = field(default_factory=list)
  eligible_wins: List[Any] = field(default_factory=list)


@dataclass
class Wins:
  ij: tuple
  row_right: tuple
  row_left: tuple
  column_right: tuple
  column_left: tuple
  diagonal_right: tuple
  diagonal_left: tuple



def create_board(data: Data) -> Data:
  '''Creates an nxn board'''
  data.board = []
  for i in range(data.n):
    for j in range(data.n):
      data.board.append(Cell(i=i, j=j))
  return data


def create_json_board(data: Data) -> Data:
  '''
  Creates a dictionary representation of a board. Dictionary keys of the json 
  are the cells, ij, of the board, and dictionary values are the state/fill of
  the cells
  '''
  data.board = {}
  for i in range(data.n):
    for j in range(data.n):
      data.board[f'{i}{j}'] = ''
  return data


def set_turn_order(data: Data) -> Data:
  '''
  Set the number and order players will take turn in. Choose random player
  followed by the next player, in that order until all turns are taken.
  '''
  players = ['x', 'o']
  index = randint(0, 1)
  for i in range(data.n**2):
    data.turn_order.append(players[index])
    if index == 1:
      index = 0
    else:
      index = 1
  return data


def get_cell_stats(data: Data) -> Data:
  ''''''
  states = ['', 'x', 'o']

  cell_stats = []
  n = len(data.board)
  
  # Get the statistics of cells by state
  for state in states:
    count = list(data.board.values()).count(state)
    percent = count / n
    cell_stats.append(Cell_Stats(
      state=state,
      count=count,
      percent=percent, 
      cells=[], ))
  
  # Get list of cells at each state
  cells_by_fill = {'': [], 'x': [], 'o': []}
  for cell in data.board:
    fill = data.board[cell]
    cells_by_fill[fill].append(cell)
  # Update the statistics from earlier with the cells at each state
  for i in range(len(cell_stats)):
    cells = cells_by_fill[cell_stats[i].state]
    cell_stats[i].cells = cells

  data.cell_stats.append(cell_stats)
  return data


@dataclass
class Points:
  row_right: List = field(default_factory=lambda: [])
  row_left: List = field(default_factory=lambda: [])
  column_right: List = field(default_factory=lambda: [])
  column_left: List = field(default_factory=lambda: [])
  diagonal_right: List = field(default_factory=lambda: [])
  diagonal_left: List = field(default_factory=lambda: [])


def get_possible_wins(data: Data) -> Data:
  '''
  Get start and end cells that make up possible row, column, and diagonal wins
  for each cell in the board
  Parameters
    n (int): Dimensions of the board
    possible_wins (List): Store lists of possible wins
  Yields
    possible_win (List): Store lists of possible wins
  '''
  store = []

  # Direction and start/end of cells that make up a win
  increments = dict(
    horizontal_right='i + length, j',
    horizontal_left='i - length, j',
    vertical_down='i, j + length',
    vertical_up='i, j - length',
    diagonal_right_down='i + length, j + length',
    diagonal_left_up='i + length, j + length',
    diagonal_right_up='i - length, j - length',
    diagonal_left_down='i + length, j + length', )
    
  # Range adjusted i,j must fall into
  ij_valid_range = list(range(0, data.n))
  # Amount to adjust i,j by
  length = data.n - 1
  
  # Get possible wins for each cell and add to store
  board_points = list(data.board.keys())
  for point in board_points:
    i =  int(point[0])
    i = int(point[1])

    # for key



    print(point)
  
  # Validate
  data.possible_wins = store
  return data
      


@dataclass
class Increment:
  direction: str = None
  i: int = 0
  j: int = 0


@dataclass
class Cell:
  i: int = 0
  j: int = 0
  # coordinates: str = '00'
  value: str = ''


ADDERS = [
  Increment(direction='horizontal_left', i=-1, j=0),
  Increment(direction='horizontal_right', i=1, j=0),
  Increment(direction='vertical_up', i=-1, j=0),
  Increment(direction='vertical_down', i=1, j=0),
  Increment(direction='diagonal_right_down', i=1, j=-1),
  Increment(direction='diagonal_right_up', i=1, j=1),
  Increment(direction='diagonal_left_down', i=-1, j=0),
  Increment(direction='diagonal_left_up', i=-1, j=-1), ]


@dataclass
class Adders:
  horizontal_right: Increment = field(default_factory = lambda: Increment(1, 0))
  horizontal_left: Increment = field(default_factory = lambda: Increment(-1, 0))
  vertical_down: Increment = field(default_factory = lambda: Increment(0, 1))
  vertical_up: Increment = field(default_factory = lambda: Increment(0, -1))
  diagonal_right_down: Increment = field(default_factory = lambda: Increment(1, -1))
  diagonal_right_up: Increment = field(default_factory = lambda: Increment(1, 1))
  diagonal_left_down: Increment = field(default_factory = lambda: Increment(-1, -1))
  diagonal_left_up: Increment = field(default_factory = lambda: Increment(-1, 1))



def get_possible_wins(data: Data) -> Data:
  ''''''

  store = []
  cells_in_a_win = []
  for adder in ADDERS:
    valid_cells = True
    i = 0
    j = 0
    cells_in_a_win = [Cell(i=i, j=j)]
    
    for k in range(data.n):
      start = cells_in_a_win[-1]
      i_adjusted = start.i + adder.i
      j_adjusted = start.j + adder.j
      print(i, j, i_adjusted, j_adjusted)
      checks = [
        i_adjusted < 0, 
        i_adjusted > data.n,
        j_adjusted < 0, 
        j_adjusted > data.n, ]
      if False in checks:
        valid_cells = False
        break
      cells_in_a_win.append(Cell(i=i_adjusted, j=j_adjusted))
    if valid_cells:
      store.append({f'{adder.direction}': cells_in_a_win})
  
  for item in store:
    print(item)

  # adders = Adders()
  # adder_names = list(asdict(adders).keys())
  # cells = list(data.board.keys())

  # for cell in cells:
  #   print(cell)
  
  # for name in adder_names:
  #   adder = getattr(adders, name)
  #   for cell in cells:
  #     i = int(cell[0])
  #     j = int(cell[0])
  #     i_adjusted = int(cell[0])
  #     j_adjusted = int(cell[0])

  #     temp = []
  #     for k in range(data.n):
  #       temp.append(Cell(i=i_adjusted, j=j_adjusted))
  #       i_adjusted += adder.j
  #       j_adjusted += adder.i
  #     print(temp)


  #     print(name, i, j)


  return data


def populate_wins_with_other_cells(data: Data) -> Data:
  ''''''
  store = []
  cells = []

  # Add to point (i, j) to get list of points that make up a win
  adders = {
    'horizontal_right': (1, 0),
    'horizontal_left': (1, 0),
    'vertical_down': (0, 1),
    'vertical_up': (0, 1),
    'diagonal_right_down': (1, 1),
    'diagonal_right_up': (1, 1),
    'diagonal_left_down': (1, 1),
    'diagonal_left_up': (1, 1), }

  for win in data.possible_wins: # win.cells datatclass attribute
    direction = list(win.keys())[0]
    adder = adders[direction]

    print(adder_direction)

    start_end_cells = list(win.values())[0]
    cells.extend(start_end_cells)

    for i in range(data.n - 1):
      adjusted_cell = (
        cells[i][0] + adder[0],
        cells[i][1] + adder[0], )
      if adjusted_cell not in cells:
        cells.append(adjusted_cell)
      else:
        break
    store.append({f'{direction}': cells})
    print({f'{direction}': cells}, win)
    cells = []
    # start_left_cells[i] += adders[i]

    
    
    # print(win)
  #   # print(cells, store)
  #   for win in data.possible_wins:
  #     print(win)


  

  # print(store)
  data.possible_wins = store
  return data


def score_cells_by_possible_wins(data: Data) -> Data:
  ''''''
  cell_scores = []

  # add 3 to i and j to see if still on board. if not exit.


  data.cell_scores = cell_scores
  return data


def take_a_turn(data: Data) -> Data:
  '''
  '''

  # Set current and next player to take a turn
  data.turn_taken.append(data.turn_order[0])
  data.turn_order.pop(0)

  data = get_cell_stats(data)
  #data = get_possible_wins(data)
  data = score_cells_by_possible_wins(data)

  # handle first move
  # print(data.cell_stats[-1][0])
  # if data.cell_stats[-1][0].percent == 1:
  #   pass

  return data


if __name__ == '__main__':
  from pprint import pprint
  import json


  data = Data(n=2)
  # data = create_board()
  data = set_turn_order(data)
  data = create_json_board(data)
  data = get_possible_wins(data)
  #data = populate_wins_with_other_cells(data)
  data = take_a_turn(data)
  
  
  # pprint(data)
  # print(json.dumps(data, indent=2))
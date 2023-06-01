import dataclasses as dc
from typing import List, Dict, Any


@dc.dataclass
class Cell:
  value: int = 0
  position: List[int] | None = None


@dc.dataclass
class Data:
  matrix: List[List[Any]] = dc.field(default_factory=lambda: [])
  adjacencies: Dict[str, List[Cell]] = dc.field(default_factory=lambda: {})
  values: List[Any] = dc.field(default_factory=lambda: [])
  connections: Dict[str, List] = dc.field(default_factory=lambda: {})
  connection_counts: Dict[str, int] = dc.field(default_factory=lambda: {})


def get_adjacent_cells(matrix: List[List[int]], cell: List[int]) -> List[Cell]:
  '''
  description:
    Returns a list of cells adjacent to a current cell
  '''
  store = []

  m = range(cell[0] - 1, cell[0] + 2)
  n = range(cell[1] - 1, cell[1] + 2)
  upper_bound_m = len(matrix)
  upper_bound_n = len(matrix[0])

  for i in m:
    # Handle position exceeding range
    if i < 0 or i >= upper_bound_m:
      continue
    for j in n:
      # Handle position exceeding range
      if j < 0 or j >= upper_bound_n:
        continue
      # Ignore current cell
      if [i, j] == cell:
        continue
      adjacent_cell = Cell(
        value=matrix[i][j], 
        # position=[i, j],
        position=f'{i}_{j}'
      )
      store.append(adjacent_cell)
  return store


def get_adjacencies_and_values(data: Data) -> Data:
  '''
  description:
    Get adjacent cells and values for each cell in the in the matrix, and all of
    the unique values in the matrix
  '''

  adjacencies = {}
  values = []

  m = len(data.matrix)
  n = len(data.matrix[0])

  for i in range(m):
    for j in range(n):
      # Get cells adjacent to the current cell
      cell = [i, j]
      adjacent_cells = get_adjacent_cells(matrix=matrix, cell=cell)
      adjacencies[f'{i}_{j}'] = adjacent_cells
      # Get unique values
      value = data.matrix[i][j]
      if value in values:
        continue
      values.append(value)
  data.adjacencies = adjacencies
  data.values = values
  return data


def get_connections(data: Data) -> Dict[str, List]:
  '''
  description:

  '''
  store = {}

  for value in data.values:
    store[value] = []

  for position in data.adjacencies.keys():
    adjacent_cells = data.adjacencies[position]
    for cell in adjacent_cells:
      # Convert position to list of integers from string
      position_ints = position.split('_')
      position_ints = [int(x) for x in position_ints]
      value = data.matrix[position_ints[0]][position_ints[1]]
      # Handle adjacent cells that don't have the same value as the current cell
      if value != cell.value:
        continue
      # Pair current and adjacent cell
      pair = [position, cell.position]
      pair.sort()
      # Handle pairs that have already been stored
      if pair in store[value]:
        continue
      store[value].append(pair)
  return store


def get_connection_counts(data: Data) -> Dict[str, int]:
  ''''''
  store = {}
  for key in data.connections.keys():
    store[key] = len(data.connections[key])
  return store


def main(data: Data) -> Dict[str, int]:
  '''
  description:

  '''
  data = get_adjacencies_and_values(data=data)
  data.connections = get_connections(data=data)
  data.connection_counts = get_connection_counts(data=data)
  return data.connection_counts


matrix = [
  ['blue', 'green', 'red'],
  ['blue', 'blue', 'green'],
  ['red', 'blue', 'green'],
  ['red', 'red', 'blue'],
]
data = Data(matrix)
data = main(data)

a = ['1_1', '0_0']
a.sort()
print(a)
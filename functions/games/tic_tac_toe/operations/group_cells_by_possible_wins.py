from dataclasses import dataclass
from typing import List


@dataclass
class Data:
  n: int = None,
  coordinates_ij: str = None
  increment_ij: str = None
  direction: str = None
  group: List[str] = None



def group_cells_by_possible_wins(data: Data | dict) -> List[str]:
  '''
  Summary
    Creates a list of cells that make up a win. 
  Inputs
    n: Size of nxn board
    cell: Cell at coordinates i,j to start from
    adder: Increment i,j of a cell
  Returns
    A list of cells that make up a win or None if cells are not on the board
  '''

  if isinstance(data, dict):
    data = Inputs(**data)

  # Store cells that forms a group for a possible win
  store = []
  # Set coordinates for the first cell in the group to the current cell
  i = int(data.coordinates_ij[0])
  j = int(data.coordinates_ij[1])

  for k in range(n):
    # Increment current cell to get cells making up the group
    i_adjusted = i + data.increment_ij[0] * k
    j_adjusted = j + data.increment_ij[1] * k
    
    # Check that the coordinates incremented cell fall within the board
    checks = [
      i_adjusted >= 0,
      j_adjusted >= 0,
      i_adjusted < n,
      j_adjusted < n, 
      adjusted_ij < f'{n}{n}']
    # Handle failed checks
    if False in checks:
      return None

    # Store incremented cell
    adjusted_ij = f'{i_adjusted}{j_adjusted}'
    store.append(adjusted_ij)
  return store
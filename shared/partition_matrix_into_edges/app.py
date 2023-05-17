

from dataclasses import dataclass, field
from typing import List, Dict
from math import floor
from copy import deepcopy

from shared.error_handler import app as error_handler
from shared.setup_data import app as setup_data


# Step from center positions to form edges
SQUARE_STEPS = {
  'even': {
    3: [
      ((1, 0), (1, 1)),
      ((0, 1), (1, 1)),
    ],
    2: [
      ((0, -1), (1, -1)),
      ((1, -1), (1, 0)),
    ],
    1: [
      ((-1, 0), (-1, 1)),
      ((-1, 1), (0, 1)),
    ],
    0: [
      ((-1, -1), (-1, 0)),
      ((-1, -1), (0, -1)),
    ],
  },
  'odd': {
    0: [
      [(-1, -1), (-1, 1)],
      [(-1, -1), (1, -1)],
      [(-1, 1), (1, 1)],
      [(1, -1), (1, 1)],
    ],
  }
}


@dataclass
class Data:
  shape: List[int] | None = None
  partitions: List[List[int]] = field(default_factory=lambda: [])
  parities: List[str] = field(default_factory=lambda: [])
  shapes: List[str] = field(default_factory=lambda: [])
  center_edges: List[List[str | int]] = field(default_factory=lambda: [])
  outer_edges: List[List[str | int]] = field(default_factory=lambda: [])
  square_steps: Dict[str, Dict[int, List]] = field(
    default_factory=lambda: SQUARE_STEPS)


def pre_processing(
  values: List[List[int]],
  shape: List[int],
) -> Data:
  # Initialize dataclass object
  if shape is not None:
    data = Data(shape=shape)
    return data
  if values is not None:
    m = len(values)
    n = len(values[0])
    data = Data(shape=[m, n])
    return data
  return None

def get_partitions(
  m: int,
  n: int,
) -> List[List[int]]:
  a, b = m, n
  position = [a, b]
  store = [[a, b]]

  if 1 in position:
    return store

  difference_n = abs(m - n)
  for k in range(difference_n):
    # Silence unused argument linting error
    _ = k

    max_index = max(a, b)
    min_index = min(a, b)
    difference = max_index - min_index
    max_index_position = position.index(max_index)

    position = [min_index]
    if max_index_position == 0:
      position = [difference] + position
    if max_index_position == 1:
      position = position + [difference]
    store.append(position)
    a, b = position
  return store


def get_parity(partition: List[int]) -> str:
  use_number = {
    1: max(partition),
    0: min(partition),
  }
  _case = 1 in partition
  number = use_number[_case]
  condition = number % 2 == 0
  return 'odd' if condition is not True else 'even'


def get_shape(partition: List[int]) -> str:
  cases = {
    1 in partition: 'array',
    1 not in partition: 'square',
  }
  shape = cases[1]
  return shape


def get_center_edges_for_array(
  m: int,
  n: int,
  parity: str,
) -> List[List[str]]:
  a = max(m, n)
  a_index = [m, n].index(a)

  b = floor((a - 1) / 2)
  c = None
  if parity == 'even':
    c = b + 1
  if parity == 'odd':
    c = b

  center = None
  if a_index == 0:
    center = [[f'{b}.0', f'{c}.0']]
  if a_index == 1:
    center = [[f'0.{b}', f'0.{c}']]
  return center


def set_shifter_for_square_center_edges(m: int, n: int) -> Dict:
  shifter = {0: 0, 1: 0}
  shift_value = abs(m - n)
  position = [m, n]
  max_position_index = position.index(max(position))
  shifter[max_position_index] = shift_value
  return shifter


def get_center_edges_for_square_even(
  m: int,
  n: int,
) -> List[List[int]]:
  shifter = set_shifter_for_square_center_edges(m=m, n=n)
  steps = [
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1],
  ]

  center_edges = []
  start = floor(min([m, n]) / 2) - 1
  steps_n = range(len(steps))
  for i in steps_n:
    a = start + steps[i][0] + shifter[0]
    b = start + steps[i][1] + shifter[1]
    center = f'{a}.{b}'
    center_edges.append([center, center])
  return center_edges


def get_center_edges_for_square_odd(
  m: int = None,
  n: int = None,
) -> List[List[int]]:
  start = floor(min(m, n) / 2)
  shifter = set_shifter_for_square_center_edges(m=m, n=n)
  a = start + shifter[0]
  b = start + shifter[1]
  position = f'{a}.{b}'
  center_edge = [[position, position]]
  return center_edge


GET_CENTER_EDGES_FOR_SQUARE = {
  'odd': get_center_edges_for_square_odd,
  'even': get_center_edges_for_square_even,
}


def get_center_edges_for_square(
  m: int,
  n: int,
  parity: str,
) -> List[List[int]]:
  function = GET_CENTER_EDGES_FOR_SQUARE[parity]
  return function(m=m, n=n)


GET_CENTER_EDGES = {
  'array': get_center_edges_for_array,
  'square': get_center_edges_for_square,
}


def get_center_edges(
  partition: List[int],
  shape: str,
  parity: str,
) -> List[List[str]]:
  m, n = partition
  function = GET_CENTER_EDGES[shape]
  return function(m=m, n=n, parity=parity)


def get_outer_edges_for_array(
  partition: List[int],
  center_edges: List[List[str]],
  parity: str = None,
  square_steps: Dict[str, dict] = None,
) -> List[List[str]]:
  # Silence unused argument linting error
  _ = parity, square_steps

  center_edges = center_edges[0]
  start = '0.0'
  end = max(partition) - 1
  if center_edges[0][0] == 0:
    end = f'0.{end}'
  if center_edges[0][0] != 0:
    end = f'{end}.0'
  half_one = [start, center_edges[0]]
  half_two = [center_edges[0], end]
  return [half_one, half_two]


# def get_outer_edges_for_square_even():
#   return


# def get_outer_edges_for_square_odd():
#   return


# GET_OUTER_EDGES_FOR_SQUARE = {
#   'odd': get_outer_edges_for_square_odd,
#   'even': get_outer_edges_for_square_even,
# }


def get_edge_corner(
  step: List[int],
  center_position: List[int],
  partition,
  i: int,
) -> str:
  a, b = step
  a = i * a + center_position[0]
  b = i * b + center_position[1]

  # Conditions to exit loop
  conditions = [
    a < 0,
    b < 0,
    a >= partition[0],
    b >= partition[1],
  ]
  edge_corner = ''
  if True not in conditions:
    edge_corner = f'{a}.{b}'
  return edge_corner


def get_outer_edges_for_square(
  partition: List[int],
  parity: str,
  center_edges: List[List[str]],
  square_steps: Dict[str, dict],
) -> List[List[str]]:
  store = []
  square_steps = square_steps[parity]

  # Ranges to iterate through
  layers_n = {
    'odd': min(partition) - 1,
    'even': min(partition) - 2,
  }
  layers_n = layers_n[parity]

  for i in range(1, layers_n):
    for j in range(len(center_edges)):
      center_position = center_edges[j][0]
      center_position = center_position.split('.')
      center_position = [
        int(center_position[0]),
        int(center_position[1]),
      ]

      quadrant_steps = square_steps[j]
      quadrant_steps_n = range(len(quadrant_steps))
      for k in quadrant_steps_n:
        store_steps = []
        for step in quadrant_steps[k]:
          edge_corner = get_edge_corner(
            step=step,
            center_position=center_position,
            partition=partition,
            i=i,
          )
          if len(edge_corner) == 0:
            break
          store_steps.append(edge_corner)

        if len(store_steps) == 0:
          continue

        store.append(store_steps)
  return store


GET_OUTER_EDGES = {
  'array': get_outer_edges_for_array,
  'square': get_outer_edges_for_square,
}


def get_outer_edges(
  partition: List[int],
  shape: str,
  parity: str,
  center_edges: List[List[str]],
  square_steps: Dict[str, dict],
) -> List[List[str]]:
  function = GET_OUTER_EDGES[shape]
  return function(
    partition=partition,
    parity=parity,
    center_edges=center_edges,
    square_steps=square_steps,
  )


def process_partitions(data: Data) -> Data:
  partitions_n = len(data.partitions)
  for i in range(partitions_n):
    partition = data.partitions[i]
    shape = get_shape(partition=partition)
    parity = get_parity(partition=partition)
    center_edges = get_center_edges(
      partition=partition,
      shape=shape,
      parity=parity,
    )
    outer_edges = get_outer_edges(
      partition=partition,
      shape=shape,
      parity=parity,
      center_edges=center_edges,
      square_steps=deepcopy(data.square_steps),
    )

    data.shapes.append(shape)
    data.parities.append(parity)
    data.center_edges.extend(center_edges)
    data.outer_edges.extend(outer_edges)
  return data


def post_processing(data: Data) -> Data:
  data = data.center_edges + data.outer_edges
  data_n = range(len(data))
  for i in data_n:
    store = []
    for position in data[i]:
      a, b = position.split('.')
      a = int(a)
      b = int(b)
      store.append([a, b])
    data[i] = store
  return data


@error_handler.main()
def main(
  data: Data | dict | str = None,
  # values: List[List[int]] = None,
  # shape: List[int] = None,
) -> List[List[List[int]]]:
  data = setup_data.main(data=data, data_class=Data)
  data.partitions = get_partitions(
    m=data.shape[0],
    n=data.shape[1],
  )
  data = process_partitions(data=data)
  data = post_processing(data=data)
  return data


def example() -> None:
  from shared.execute_example_data import app as execute_example_data


  examples = [
    'shape: [1, 1]',
    'shape: [4, 1]',
    'shape: [4, 4]',
    'shape: [5, 5]',
    'shape: [3, 3]',
    'shape: [4, 3]',
    'shape: [5, 4]',
    'shape: [6, 5]',
  ]
  execute_example_data.main(
    examples=examples,
    main_function=main,
  )


if __name__ == '__main__':
  example()

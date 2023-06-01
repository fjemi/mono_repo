import dataclasses as dc
from os import path
from typing import List, Dict
from time import time
import json
import requests

from functions.games.sudoku import app as sudoku
from shared.get_environment import app as get_environment
# from shared.error_handler import app as error_handler


ENV = get_environment.main(module_path=__file__)
URL = 'https://raw.githubusercontent.com/maxbergmark/sudoku-solver/master/data-sets/all_17_clue_sudokus.txt'


@dc.dataclass
class FilePaths:
  inputs: str | None = None
  grids: str | None = None
  outputs: str | None = None


@dc.dataclass
class Benchmark:
  total_time_s: float = 0
  count: int = 0
  average_time_s: float = 0


@dc.dataclass
class Data:
  url: str = URL
  data_path: str = dc.field(default_factory=lambda: ENV.DATA_PATH)
  file_paths: FilePaths | None = None
  n: int = 9
  benchmark: Benchmark | None = None


class Store:
  pass


def set_file_paths(data: Data) -> Data:
  file_paths = FilePaths()
  for field in dc.fields(file_paths):
    file_path = f'sudoku/{field.name}.txt'
    file_path = path.join(data.data_path, file_path)
    setattr(file_paths, field.name, file_path)
  data.file_paths = file_paths
  return data


def check_if_input_file_exists(file_path: str) -> bool:
  return path.exists(file_path)


def get_inputs_from_source(url: str) -> str:
  response = requests.get(url)
  if response.status_code != 200:
    raise RuntimeException()
  return response.text


def get_blank_grid(n: int) -> Dict[str, None]:
  store = {}

  for i in range(n):
    for j in range(n):
      position = f'{i}.{j}'
      store[position] = None
  return store


def convert_string_grid_to_dictionary(
  grid: str,
  n: int,
) -> Dict:
  store = get_blank_grid(n=n)
  
  chars_n = len(grid)
  keys = list(store.keys())
  for i in range(chars_n):
    key = keys[i]
    value = int(grid[i])
    store[key] = value
  return store


def save_grids_to_file(
  file_path: str,
  grids: List[Dict],
) -> bool:
  with open(file_path, 'w+') as file:
    for grid in grids:
      file.write(json.dumps(grid) + '\n')
  return True


def format_inputs_as_grids(inputs: str, n: int) -> List[dict]:
  inputs = inputs.split('\n')
  count = inputs[0]
  puzzles = inputs[1:]

  store = []
  for grid in puzzles:
    grid = convert_string_grid_to_dictionary(grid=grid, n=n)
    store.append(grid)
  return store


def get_and_format_puzzle_inputs(data: Data) -> bool:
  check = check_if_input_file_exists(file_path=data.file_paths.grids)
  if check is False:
    inputs = get_inputs_from_source(url=data.url)
    grids = format_inputs_as_grids(inputs=inputs, n=data.n)
    save_grids_to_file(
      file_path=data.file_paths.grids,
      grids=grids,
    )
  return True


def benchmark_app(data: Data) -> Benchmark:
  benchmark = Benchmark()
  with open(
    file=data.file_paths.grids, 
    mode='r',
    encoding='utf-8'
  ) as file:
    total_time = 0
    count = 0
    for line in file:
      count += 1
      grid = json.loads(line)
      start_time = time()
      result = sudoku.main(grid=grid)
      run_time = time() - start_time
      total_time += run_time
      average_time = round(total_time / count, 2)

  benchmark = Benchmark(
    count=count,
    total_time_s=round(total_time, 2),
    average_time_s=round(average_time, 2),
  )
  return benchmark


# error_handler.main()
def main(data: Data) -> Benchmark:
  data = set_file_paths(data=data)
  status = get_and_format_puzzle_inputs(data=data)
  if status is not True:
    raise RuntimeError('Puzzle inputs cannot be obtained')
  data.benchmarks = benchmark_app(data=data)
  return data.benchmark


def example() -> None:
  data = Data()
  main(data=data)


if __name__ == '__main__':
  example()
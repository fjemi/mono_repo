from exception_handler import exception_handler

from dataclasses import dataclass


@dataclass
class Data:
  a: int = 0
  b: int = 0
  operation: str = 'add'
  result: int = 0


@exception_handler
def add(data: Data):
  data.result = data.a + data.b
  return data


if __name__ == '__main__':
  dataset = [Data(a=1, b=1), Data(a=1, b=None)]
  for data in dataset:
    result = add(data)
    print(result)
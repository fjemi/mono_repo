from dataclasses import dataclass
import math

@dataclass
class Data:
  a: int = 0
  b: int = 0


def main(data: Data | dict) -> int:
  if isinstance(data, dict):
    data = Data(**data)
  return data.a + data.b


def add(a: int | float, b: int | float) -> int:
  return a + b


def floor(a: int | float) -> int:
  return math.floor(a)


data = Data(1, 2)
c = main(data)
print(c)
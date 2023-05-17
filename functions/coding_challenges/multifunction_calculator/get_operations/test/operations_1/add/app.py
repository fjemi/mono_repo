from dataclasses import dataclass


@dataclass
class Data:
  a: int = 0
  b: int = 0


def calculate_add(data: Data) -> int:
  return data.a + data.b

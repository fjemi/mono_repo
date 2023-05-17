from dataclasses import dataclass


@dataclass
class Data:
  a: float | int = 0
  b: float | int = 0
  result: float | int = 0


def add(data: Data) -> Data:
  data.result = data.a + data.b
  return data


def subtract(data: Data) -> Data:
  data.result =  data.b - data.a
  return data


def use_add(a: int, b: int) -> Data:
  data = Data(a=a, b=b)
  return add(data=data)


def use_subtract(a: int, b: int) -> Data:
  data = Data(a=a, b=b)
  return subtract(data=data)


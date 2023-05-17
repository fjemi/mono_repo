from dataclasses import dataclass
from dacite import from_dict


@dataclass
class Data:
  a: int = None
  b: int = None


def add(data: Data) -> int:
  '''Adds two integers'''
  if isinstance(data, dict):
    data = from_dict(data=data, data_class=Data)
  return data.a + data.b


if __name__ == '__main__':
  data = Data(a=1, b=1)
  data = add(data)
  print(data)
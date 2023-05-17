from dataclasses import dataclass
from typing import Union


@dataclass
class Data:
  pass


def main(data: Union[Data, dict]) -> Data:
  return data

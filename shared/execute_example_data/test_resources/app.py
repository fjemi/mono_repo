#!/usr/bin/env python3

from dataclasses  import dataclass

from shared.setup_data import app as setup_data


@dataclass
class Data:
  a: int = 0
  b: int = 0
  result: int = 0
  return_result: bool = False


def main(data: Data | dict | str) -> Any:
  data = setup_data.main(data=data)
  data.result = data.a + data.b
  if data.return_result is True:
    return data.result
  return data

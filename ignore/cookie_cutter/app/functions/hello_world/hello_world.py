#!/usr/bin/env python3

# Standard packages
from dataclasses import dataclass, asdict
from os.path import dirname


@dataclass
class Data:
  hello: str = 'world'


def hello_world(data: Data = Data()) -> Data:
  '''
  Description
    A hello world example
  Parameters:
    hello: The person or thing to greet
  Returns
    A hello world greeting
  '''

  if data is None:
    return Data()

  # Unpack dictionary into dataclass
  if isinstance(data, dict):
    data = Data(**data)

  if len(data.hello) == 0:
    data = Data()

  return asdict(data)


def example():
  '''Example usage'''
  result = main()
  print(result)


if __name__ == '__main__':
  example()

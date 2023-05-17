# Standard
from dataclasses import dataclass
from typing import List, Union, Optional
# Internal
from functions.exception_handler.exception_handler import exception_handler


@dataclass
class Data:
  '''
  Summary
    Store data for performing arthmetic operations
  Attributes
    a: A number
    b: A number
    operation: The arthimitic operation performed on `a` and `b`
    result: The result of the operation
  '''
  a: Union[List[Union[int, float]], Union[int, float]] = None
  b: Union[List[Union[int, float]], Union[int, float]] = None
  operation: str = None
  result: Union[int, float] = None


@exception_handler
def data_setup(data: Union[Data, dict]) -> Optional[Data]:
  if isinstance(data, dict):
    data = Data(**data)

  # Add single numbers to lists to facilitate later operations
  if not isinstance(data.a, list):
    data.a = [data.a]
  if not isinstance(data.b, list):
    data.b = [data.b]
  return data


@exception_handler
def add(data: Union[Data, dict]) -> Optional[Data]:
  data = data_setup(data)
  data.result = sum(data.a + data.b)
  data.operation = 'add'
  return data


# @exception_handler
def subtract(data: Union[Data, dict]) -> Optional[Data]:
  data = data_setup(data)
  store = data.a + data.b
  data.result = store[0]
  for i in range(1, len(store)):
    data.result = data.result - store[i]
  data.operation = 'subtract'
  return data


@exception_handler
def multiply(data: Union[Data, dict]) -> Optional[Data]:
  data = data_setup(data)
  store = data.a + data.b
  data.result = store[0]
  for i in range(1, len(store)):
    data.result = data.result * store[i]
  data.operation = 'multiply'
  return data


@exception_handler
def divide(data: Union[Data, dict]) -> Optional[Data]:
  data = data_setup(data)
  store = data.a + data.b
  data.result = store[0]
  for i in range(1, len(store)):
    data.result = data.result / store[i]
  data.operation = 'divide'
  return data


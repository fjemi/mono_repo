
from dataclasses import dataclass, is_dataclass
from typing import Any
# Internal
from functions.type_handler.type_handler import type_handler
from functions.exception_handler.exception_handler import exception_handler


@dataclass(slots=True)
class Data:
  string: str = None
  integer: int = None
  store: list = None


def type_handler_test() -> None:
  '''Tests that the functions handles data of different types correctly'''
  
  # Test cases
  cases = [
    dict(
      data='',
      data_class=Data, 
      expected=Data(string=''), ),
    dict(
      data=None, 
      data_class=Data,
      expected=None, ),
    dict(
      data=None, 
      data_class=Data,
      expected=Data(), 
      instaniate_data_class=True, ),
    dict(
      data=[], 
      data_class=Data, 
      expected=Data(string=[]), ),
    dict(
      data=1, 
      data_class=Data, 
      expected=Data(string=1), ),
    dict(
      data={}, 
      data_class=Data, 
      expected=Data(), ),
    dict(
      data={'string': []}, 
      data_class=Data, 
      expected=Data(string=[]), ),
    dict(
      data={'string': [], 'integer': 1}, 
      data_class=Data, 
      expected=Data(string=[], integer=1), ), ]

  # 
  for case in cases:
    output = type_handler(**case)
    assert output == case['expected']

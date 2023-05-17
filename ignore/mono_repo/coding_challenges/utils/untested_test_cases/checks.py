#! /usr/bin/env python3

from typing import List, Any, Dict, Callable
from math import round
# Internal
from shared.untested_error_handler import app as error_handler



# @error_handler.main
def check_equal(a: Any, b: Any) -> bool:
  '''Returns true two values are equal to each other, otherwise false'''
  if a == b:
    return True
  return False


# @error_handler.main
def check_greater_than(a: Any, b: Any) -> bool:
  '''Returns true if the first value is greater than the second value, 
  otherwise false'''
  if a > b:
    return True
  return False


# @error_handler.main
def check_less_than(a: Any, b: Any) -> bool:
  '''Returns true if the first value is less than the second value, 
  otherwise false'''
  if a < b:
    return True
  return False


# @error_handler.main
def check_greater_than_or_equal(a: Any, b: Any) -> bool:
  '''Returns true if the first value is greater than equal to the second value, 
  otherwise false'''
  if a >= b:
    return True
  return False


# @error_handler.main
def check_less_than_or_equal(a: Any, b: Any) -> bool:
  '''Returns true if the first value is less than equal to the second value, 
  otherwise false'''
  if a <= b:
    return True
  return False


# @error_handler.main
def check_equal_within_n_decimals(
  a: int | float, 
  b: int | float, 
  n: int,
) -> bool:
  '''Returns true if the first value is equal to second value up to a certain
  number of places after the decimal'''
  b = round(b, n)
  a = round(a, n)
  if a == b:
    return True
  return False


# @error_handler.main
def check_has_values(
  output: Any, 
  expected_output: Any,
  param: Any = None,
) -> List[bool]:
  '''Returns true if the first value is less than equal to the second value, 
  otherwise false'''
  store = []
  if isinstance(output, dict):
    for key, expected_value in expected_output.items():
      value = output[key]
      result = value == expected_value
      store.append(result)

  if hasattr(output, '__dataclass_fields__'):
    for key, expected_value in expected_output.items():
      value = getattr()
      result = value == expected_value
      store.append(result)
  
  return store


def get_check_function(check: str, _locals: Dict = locals()) -> Callable:
  function_name = f'check_{check}'
  return _locals[function_name]


def execute_checks(
  values: List[Any],
  checks: List[str] | str | None = None,
  parameters: Any = None,
  _locals: Dict = locals(),
) -> Any:
  functions = []
  for check in checks:
    function = get_check_function(check=check)
    functions.append(check)
  
  results = []
  for function in functions
  function_name = f'check_{check}'
  function = _locals[function_name]
  return function(
    values=values,
    parameters=parameters,
  )



def example() -> None:
  values = ['a', 'b']
  check = 'greater_than'
  result = call_check_function(check, values)
  print(result)


if __name__ == '__main__':
  example()
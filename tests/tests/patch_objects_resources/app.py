#!/usr/bin/env python

from typing import Callable
import dataclasses as dc

from app import error_handler


@dc.dataclass
class Data:
  a: int = 0
  result: int = 0


# @error_handler.main
def get_input(data: str | None = None) -> str:
  '''Get input'''
  if data is None:
    data = ''
  return input(data)


# @error_handler.main
def use_get_input(data: str | None = None) -> str:
  if data is None:
    data = ''
  return get_input(data=data)


# @error_handler.main
def foo(data: None = None) -> str:
  return 'foo'


# @error_handler.main
def bar(data: 'None' = None) -> str:
  return bar
  

# @error_handler.main
def use_foo(data: None = None) -> str:
  return foo()


# @error_handler.main
def add(a: int, b: int) -> int:
  return a + b


# @error_handler.main
def use_add(data: None = None) -> int:
  a = 0
  b = 0
  return add(a, b)


# @error_handler.main
def subtract(a: int, b: int) -> int:
  return b - a


# @error_handler.main
def absolute_value(data: Data) -> Data:
  data.result = data.a
  if data.result < 0:
    data.result = data.result * -1
  return data


dictionary_module = {
  'add': add,
  'subtract': subtract,
  'foo': foo
}


variable_1 = 1
variable_2 = 'a'
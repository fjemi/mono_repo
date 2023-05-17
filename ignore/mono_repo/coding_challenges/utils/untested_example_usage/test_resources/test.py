from pydantic import BaseModel
from pydantic.dataclasses import dataclass as pydantic_dataclass
from dataclasses import dataclass as standard_dataclass
from types import ModuleType


@standard_dataclass
class Data_1:
  a: int = None
  b: int = None


class Data_2(BaseModel):
  a: int = None
  b: int = None


@pydantic_dataclass
class Data_3:
  a: int = None
  b: int = None


Data_4 = str


def add(a, b):
  return a + b


def use_add(a, b):
  return add(a, b)


def get_input():
  return input()


def use_get_input():
  return get_input()
  
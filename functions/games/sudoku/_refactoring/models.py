#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict


@dc.dataclass
class Position:
  # columns:
  # rows:
  # intersections: 
  ...


@dc.dataclass
class Groups:
  n: int = 0
  branch: str | None = None
  grid: Dict[str, str | float] = dc.field(
    default_factory=lambda: {})
  rows: List[List[str] | float] = dc.field(
    default_factory=lambda: [])
  columns: List[List[str] | float] = dc.field(
    default_factory=lambda: [])
  intersections: Dict[str, List[str] | float] = dc.field(
    default_factory=lambda: {})
  values: Dict[str, str | float] = dc.field(
    default_factory=lambda: {})
  valid: bool = True


@dc.dataclass
class Data:
  grid: List[List[str | int]] | None = None
  positions: Groups | None = None
  tree: List[List[str]] | None = None
  completed: List[List[str]] | None = None
  completed_values_total: int = 0


@dc.dataclass
class Base:
  n: int = 0
  columns: List[List[int | int] | float] | None = None
  rows: List[List[int | int] | float] | None = None
  intersections: Dict[str, List[str | int] | float] | None = None
  values: Dict[str, List[str | int] | float] | None = None


class Store:
  pass


# @dc.dataclass
# class Group:
#   positions: Dict[str, int] | List[List[int]] | None = None
#   values: Dict[str, List[int]] | List[List[int]] | None = None
#   available_values: Dict[str, List[int]] | List[List[int]] | None = None
#   scores: Dict[str, float] | None = None


# @dc.dataclass
# class Groups:
  # n: int = 0
  # grid: Dict[str, int] | None = None
#   rows: Group = dc.field(default_factory=lambda: Group())
#   columns: Group = dc.field(default_factory=lambda: Group())
#   intersections: Group = dc.field(default_factory=lambda: Group())
  
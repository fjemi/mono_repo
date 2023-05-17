#!/usr/bin/env python3

# Internal Packages
import hello_world
# Standard Library
from dataclasses import asdict


def test_hello_world() -> None:
  #
  output = hello_world.hello_world()
  expected = {'hello': 'world'}
  assert asdict(output) == expected

  #
  data = {'hello': 'jane'}
  output = hello_world.world(data)
  expected = {'hello': 'jane'}
  assert asdict(output) == expected

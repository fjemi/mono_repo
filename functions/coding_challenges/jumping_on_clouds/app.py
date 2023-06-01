#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  clouds: List[int] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  safe_cloud_positions: List[int] = dc.field(default_factory=lambda: [])
  jumps: Dict[int, List[int]] = dc.field(default_factory=lambda: {})
  jump_count: int = 0


def get_safe_cloud_positions(data: Data) -> List[int]:
  positions = []
  n = len(data.body.clouds)
  for i in range(n):
    cloud = data.body.clouds[i]
    # Handle clouds to avoid
    if cloud == 1:
      continue
    # Handle safe clouds
    positions.append(i)
  return positions


def get_jumps(data: Data) -> Dict[int, List[int]]:
  # Handle there being no safe clouds to jump to
  if len(data.safe_cloud_positions) == 0:
    return {0: []}

  # Keys are clouds that have been jumped to.
  # Values are a list of possible clouds to jump to.
  jumps = {data.safe_cloud_positions[0]: []}
  n = len(data.safe_cloud_positions)
  final_cloud = data.safe_cloud_positions[-1]

  # Loop until we have jumped to the last cloud
  while final_cloud not in jumps:
    keys = list(jumps.keys())
    jump = keys[-1]
    # Get a list of safe clouds to jump to
    # next from the current cloud
    for i in range(n - 1):
      next_cloud = data.safe_cloud_positions[i + 1]
      distance = next_cloud - jump
      if distance not in [1, 2]:
        continue
      jumps[jump].append(next_cloud)

    # Jump to the last cloud in the list of safe clouds
    new_key = jumps[jump][-1]
    jumps[new_key] = []

  return jumps


async def get_response(data: Data) -> dict:
  return dict(
    jumps=data.jumps,
    n=data.jump_count,
  )


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  clouds: List[int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.safe_cloud_positions = get_safe_cloud_positions(data=data)
  data.jumps = get_jumps(data=data)
  data.jump_count = len(data.jumps.keys()) - 1
  data = await get_response(data=data)
  return data

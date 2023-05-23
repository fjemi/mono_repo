#!usr/bin/env python3

from dataclasses import dataclass, field, fields
from typing import List, Dict, Callable


@dataclass
class Inputs:
  principal: float | None = None
  rate: float | None = None
  time: float | None = None
  time_ordinal: str = 'years'
  accrued: float | None = None
  total_accrued: float = None


@dataclass
class Data:
  inputs: Dict | Inputs = None
  operation: str | None = None
  result: int | float = None


async def calculate_principal(data: Data) -> Data:
  denominator = data.inputs.accrued / (
    1 + data.inputs.rate * data.inputs.time)
  data.result = data.inputs.accrued / denominator
  return data


async def calculate_rate(data: Data) -> Data:
  fraction = data.inputs.accrued / data.inputs.principal
  data.result = (fraction - 1) / data.inputs.time
  return data


async def calculate_time(data: Data) -> Data:
  fraction = data.inputs.accrued / data.inputs.principal
  data.result = (fraction - 1) / data.inputs.rate
  return data


async def calculate_accrued(data: Data) -> Data:
  data.result = data.inputs.principal * (
    1 + data.inputs.rate * data.inputs.time)
  return data


async def calculate_total_accrued(data: Data) -> Data:
  data.result = data.inputs.principal + data.inputs.accrued
  return data


OPERATIONS = {
  'simple_interest.rate': calculate_rate,
  'simple_interest.time': calculate_time,
  'simple_interest.principal': calculate_principal,
  'simple_interest.accrued': calculate_accrued,
  'simple_interest.total_accrued': calculate_total_accrued,
}


# pylint: disable=redefined-outer-name
async def main(
  inputs: dict,
  operation: str,
) -> float | int:
  inputs = Inputs(**inputs)
  data = Data(inputs=inputs, operation=operation)
  operation = OPERATIONS[operation]
  data = await operation(data=data)
  return data


if __name__ == '__main__':
  import asyncio


  inputs = {
    'rate': 1,
    'time': 1,
    'accrued': 1,
  }
  result = asyncio.run(main(
    inputs=inputs,
    operation='simple_interest.principal',
  ))
  print(result)

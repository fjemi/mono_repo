#!usr/bin/env python3

from typing import List, Callable
import dataclasses as dc


@dc.dataclass
class Data:
  inputs: List[int | float | List] | None = None
  operation: str | Callable | None = None
  result: List[int | float] | float | int | None = None


PARITY = {
  'positive': lambda a: a,
  'negative': lambda a: a * -1,
}


async def absolute_value(a: int | float) -> int | float:
  cases = 'negative' if a <= 0 else 'positive'
  switcher = PARITY[cases]
  result = switcher(a=a)
  return result


OPERATIONS = {
  'absolute_value': absolute_value,
}


async def handle_number(data: Data) -> Data:
  operation = OPERATIONS[data.operation]
  data.result = await operation(a=data.inputs)
  return data


async def handle_array(data: Data) -> Data:
  operation = OPERATIONS[data.operation]
  store = []
  for num in data.inputs:
    num = await operation(a=num)
    store.append(num)
  data.result = store
  return data


HANDLERS = {
  'number': handle_number,
  'array': handle_array,
}


async def main(
  inputs: List[int | float] | int | float,
  operation: str,
) -> List[int | float] | int | float:
  data = Data(inputs=inputs, operation=operation)
  cases = 'array' if isinstance(data.inputs, list) else 'number'
  handler = HANDLERS[cases]
  data = await handler(data=data)
  return data.result

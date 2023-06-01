#!usr/bin/env python3

from typing import List
import dataclasses as dc


@dc.dataclass
class Data:
  inputs: List[int | float | List] | None = None
  operation: str | None = None
  result: List[int | float] | float | int | None = None


async def operation(a: int | float, b: int | float) -> int | float:
  return a / b


async def handle_numbers(data: Data) -> Data:
  store = data.inputs[0]
  for num in data.inputs[1:]:
    store = await operation(store, num)
  data.result = store
  return data


async def handle_arrays(data: Data) -> Data:
  store = data.inputs[0]
  n = len(store)
  for array in data.inputs[1:]:
    for i in range(n):
      store[i] = await operation(store[i], array[i])
  data.result = store
  return data


HANDLERS = {
  'numbers': handle_numbers,
  'arrays': handle_arrays,
}


async def main(
  inputs: List[List[float | int]] | int | float,
  operation: str,
) -> List[float | int] | int | float:
  data = Data(inputs=inputs, operation=operation)
  cases = 'arrays' if isinstance(inputs[0], list) else 'numbers'
  handler = HANDLERS[cases]
  data = await handler(data=data)
  return data.result

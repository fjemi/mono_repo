#!/usr/bin/env python3

import dataclasses as dc
from typing import List
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  operations: List[str | int] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  record: str | None = None
  total_score: int = 0


async def process_int_operation(
  operation: int,
  store: List[int],
) -> List[int]:
  return store + [operation]


async def case_operation_plus(store: List[int]) -> List[int]:
  score = sum(store[-2:])
  store.append(score)
  return store


async def case_operation_c(store: List[int]) -> List[int]:
  return store[:-1]


async def case_operation_d(store: List[int]) -> List[int]:
  score = store[-1] * 2
  store.append(score)
  return store


PROCESS_STR_OPERATION = {
  'C': case_operation_c,
  'D': case_operation_d,
  '+': case_operation_plus
}


async def process_str_operation(operation: str, store: List[int]) -> List[int]:
  function = PROCESS_STR_OPERATION[operation]
  result = await function(store=store)
  return result


async def get_record(operations: List[int | str], _locals: dict = locals()) -> List[int]:
  store = []
  for operation in operations:
    conditions = {
      isinstance(operation, int): 'int',
      isinstance(operation, str): 'str',
    }
    _case = conditions[1]
    function_name = f'process_{_case}_operation'
    function = _locals[function_name]
    store = await function(operation=operation, store=store)
  return store


async def get_total_score(record: List[int]) -> int:
  return sum(record)


async def get_response(data: Data) -> dict:
  return {'total_score': data.total_score}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  operations: List[str | int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.record = await get_record(operations=data.body.operations)
  data.total_score = await get_total_score(record=data.record)
  data = await get_response(data=data)
  return data

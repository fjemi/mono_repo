#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Any
import dacite

from api import models as api_models


@dataclass
class Body:
  values: List[Any] | None = None
  linked_list: dict | None = None
  api_response: bool = True


@dataclass
class Node:
  value: Any | None = None
  next_node: Node | None = None


@dataclass
class LinkedList:
  head: Node | None = None


@dataclass
class Data:
  body: Body | None = None
  linked_list: LinkedList | dict | None = None
  values: List[Any] | None = None
  cases: str | None = None


async def convert_list_to_linked_list(data: Data) -> Data:
  data.linked_list = LinkedList()

  if len(data.body.values) == 0:
    return data

  head = Node(value=data.body.values[0])
  current_node = head
  for value in data.body.values[1:]:
    current_node.next_node = Node(value=value)
    current_node = current_node.next_node
  data.linked_list.head = head
  return data


async def convert_dictionary_to_linked_list(
  linked_list: dict | LinkedList,
) -> LinkedList:
  if not isinstance(linked_list, dict):
    return linked_list
  linked_list = dacite.from_dict(
    data_class=LinkedList,
    data=linked_list,
  )
  return linked_list


async def convert_linked_list_to_list(data: Data) -> Data:
  data.values = []

  data.body.linked_list = await convert_dictionary_to_linked_list(
    linked_list=data.body.linked_list)

  if data.body.linked_list == Node():
    return data.values

  current_node = data.body.linked_list.head
  while current_node:
    data.values.append(current_node.value)
    current_node = current_node.next_node
  return data


ACTION_MAPPER = {
  'values': 'linked_list',
  'linked_list': 'values',
}


async def get_response(data: Data) -> dict:
  action = ACTION_MAPPER[data.cases]
  result = getattr(data, action)

  # Cases where the module is imported into another module
  if data.body.api_response is False:
    return result

  if action == 'linked_list':
    result = asdict(result)
  data = {action: result}
  return data


ACTION_SWITCHER = {
  'values': convert_list_to_linked_list,
  'linked_list': convert_linked_list_to_list,
}


async def process_request_arg(_locals: dict) -> Data:
  body = _locals['request'].data.body
  body = Body(**asdict(body))
  data = Data(body=body)
  return data


async def process_values_arg(_locals: dict) -> Data:
  body = Body(values=_locals['values'], api_response=False)
  data = Data(body=body)
  return data


async def process_linked_list_arg(_locals: dict) -> Data:
  body = Body(linked_list=_locals['linked_list'], api_response=False)
  data = Data(body=body)
  return data


MAIN_ARGS_SWITCHER = {
  'request': process_request_arg,
  'values': process_values_arg,
  'linked_list': process_linked_list_arg,
}


async def process_main_args(_locals: dict) -> Data:
  cases = []
  for key, value in _locals.items():
    _case = key * int(value is not None)
    cases.append(_case)
  cases = ''.join(cases)
  switcher = MAIN_ARGS_SWITCHER[cases]
  data = await switcher(_locals=_locals)
  return data


# pylint: disable=unused-argument
async def main(
  request: api_models.Request | None = None,
  values: List[Any] | None = None,
  linked_list: LinkedList | None = None,
) -> dict | LinkedList | List[Any]:
  data = await process_main_args(_locals=locals())
  data.cases = 'values' if data.body.values else 'linked_list'
  switcher = ACTION_SWITCHER[data.cases]
  data = await switcher(data=data)
  data = await get_response(data=data)
  return data

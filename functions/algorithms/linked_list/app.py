#!/usr/bin/env python3

from __future__ import annotations
import dataclasses as dc
from typing import List, Any
import dacite
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  values: List[Any] | None = None
  linked_list: dict | None = None


@dc.dataclass
class Node:
  value: Any | None = None
  next_node: Node | None = None


@dc.dataclass
class LinkedList:
  head: Node | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  linked_list: LinkedList | dict | None = None
  values: List[Any] | None = None
  response: LinkedList | dict | List[Any] | None = None
  cases: str | None = None
  call_method: str | None = None


async def convert_list_to_linked_list(data: Data) -> Data:
  linked_list = LinkedList()

  if len(data.body.values) == 0:
    return linked_list

  head = Node(value=data.body.values[0])
  current_node = head
  for value in data.body.values[1:]:
    current_node.next_node = Node(value=value)
    current_node = current_node.next_node
  linked_list.head = head

  data.response = linked_list
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
  return


async def convert_linked_list_to_list(data: Data) -> Data:
  store = []

  data.body.linked_list = await convert_dictionary_to_linked_list(
    linked_list=data.body.linked_list)

  if data.body.linked_list == Node():
    return store

  current_node = data.body.linked_list.head
  while current_node:
    store.append(current_node.value)
    current_node = current_node.next_node

  data.response = store
  return data


ACTION_MAPPER = {
  'values': 'linked_list',
  'linked_list': 'values',
}


async def get_response(data: Data) -> dict:
  action = ACTION_MAPPER[data.cases]

  # Cases where the module is imported into another module
  if data.call_method == 'module':
    return data.response

  if action == 'linked_list':
    data.response = dc.asdict(data.response)
  data = {action: data.response}
  return data


ACTION_SWITCHER = {
  'values': convert_list_to_linked_list,
  'linked_list': convert_linked_list_to_list,
}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  values: List[Any] | None = None,
  linked_list: dict | LinkedList | None = None,
) -> dict | LinkedList | List[Any]:
  # data = await process_main_args(_locals=locals())
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.cases = 'values' if data.body.values else 'linked_list'
  switcher = ACTION_SWITCHER[data.cases]
  data = await switcher(data=data)
  data = await get_response(data=data)
  return data

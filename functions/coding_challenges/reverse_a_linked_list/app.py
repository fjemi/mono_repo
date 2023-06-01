#!usr/bin/env python3

from typing import Any, List
import dataclasses as dc
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments
from functions.algorithms.linked_list import app as linked_list_algorithms
from functions.algorithms.linked_list.app import LinkedList, Node


@dc.dataclass
class Body:
  items: List[Any] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  linked_list: LinkedList = None
  reversed_items: List[Any] | None = None


async def reverse_linked_list(linked_list: LinkedList) -> LinkedList:
  store = Node()
  if linked_list == LinkedList():
    return store

  current_node = linked_list.head
  store.value = current_node.value

  while current_node is not None:
    current_node = current_node.next_node
    if not current_node:
      break
    store = Node(
      value=current_node.value,
       next_node=store,
    )

  store = LinkedList(head=store)
  return store



async def get_response(data: Data) -> dict:
  return {'reversed_items': data.reversed_items}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  items: List[Any] | None = None
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data.linked_list = await linked_list_algorithms.main(
    values=data.body.items)
  data.linked_list = await reverse_linked_list(linked_list=data.linked_list)
  data.reversed_items = await linked_list_algorithms.main(
    linked_list=data.linked_list)
  data = await get_response(data=data)
  return data

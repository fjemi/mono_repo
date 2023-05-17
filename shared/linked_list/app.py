#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Any
import yaml


@dataclass
class Node:
  value: Any | None = None
  next_node: Node | None = None


@dataclass
class LinkedList:
  head: Node | None = None


async def convert_list_to_linked_list(
  values: List[Any],
  *args,
  **kwargs,
) -> LinkedList:
  _ = args, kwargs

  linked_list = LinkedList()
  if len(values) == 0:
    return linked_list

  head = Node(value=values[0])
  current_node = head
  for value in values[1:]:
    current_node.next_node = Node(value=value)
    current_node = current_node.next_node
  linked_list.head = head
  return linked_list


async def convert_linked_list_to_list(
  linked_list: LinkedList,
  *args,
  **kwargs,
) -> List[Any]:
  _ = args, kwargs
  store = []

  if linked_list == Node():
    return store

  current_node = linked_list.head
  while current_node:
    store.append(current_node.value)
    current_node = current_node.next_node
  return store


async def main(
  function: str,
  values: List[Any] | None = None,
  linked_list: LinkedList | None = None,
  _locals: dict = locals(),
) -> List[Any] | LinkedList:
  function = _locals[function]
  result = await function(
    values=values,
    linked_list=linked_list,
  )
  return result


if __name__ == '__main__':
  import asyncio


  result = asyncio.run(main(
    values=[1, 2, 3 ,4, 5],
    function='convert_list_to_linked_list',
  ))
  print(result)

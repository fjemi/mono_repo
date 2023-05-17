#!usr/bin/env python3

from dataclasses import dataclass, asdict, field, fields
from typing import Any, List, Dict
import yaml

from api import models
from functions.algorithms.linked_list.app import Node, LinkedList
from functions.algorithms.linked_list import app as algorithms_linked_list


# Map list name to linked list name
NAME_MAPPER = {
  'list1': 'one',
  'list2': 'two',
}


@dataclass
class Base1:
  _list: str | LinkedList | None = None
  _linked_list: str | LinkedList | None = None


@dataclass
class Values(Base1):
  ...


@dataclass
class Names(Base1):
  ...


@dataclass
class Base2:
  one: LinkedList | Node | None = None
  two: LinkedList | Node | None = None
  merged: LinkedList | Node | None = None


@dataclass
class LinkedLists(Base2):
  ...


@dataclass
class CurrentNodes(Base2):
  ...


@dataclass
class Body(models.Body):
  list1: List[Any] | None = None
  list2: List[Any] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  name_mapper: Dict[str, str] = field(default_factory=lambda: NAME_MAPPER)
  linked_lists: LinkedLists | None = None
  current_nodes: CurrentNodes | None = None
  exit_loop: bool = False
  merged_list: List[Any] | None = None


# pylint: disable=protected-access
async def get_linked_lists(data: Data) -> Data:
  data.linked_lists = LinkedLists()
  values = Values()

  for names in data.name_mapper.items():
    names = Names(*names)
    values._list = getattr(data.body, names._list)
    # Convert list to linked list
    values._linked_list = await algorithms_linked_list.main(
      values=values._list)
    setattr(
      data.linked_lists,
      names._linked_list,
      values._linked_list,
    )

  data.linked_lists.merged = LinkedList(head=Node())
  return data


async def set_current_nodes(data: Data) -> Data:
  data.current_nodes = CurrentNodes()
  for _field in fields(data.linked_lists):
    node = getattr(data.linked_lists, _field.name).head
    setattr(data.current_nodes, _field.name, node)
  return data


async def update_current_merged_node(data: Data, node: Node) -> Data:
  data.current_nodes.merged.next_node = node
  data.current_nodes.merged = data.current_nodes.merged.next_node
  return data


async def handle_both_nodes_being_none(data: Data) -> Data:
  data.exit_loop = True
  return data


async def handle_node_two_being_none(data: Data) -> Data:
  node = Node(value=data.current_nodes.one.value)
  data.current_nodes.one = data.current_nodes.one.next_node
  data = await update_current_merged_node(data=data, node=node)
  return data


async def handle_node_one_being_none(data: Data) -> Data:
  node = Node(value=data.current_nodes.two.value)
  data.current_nodes.two = data.current_nodes.two.next_node
  data = await update_current_merged_node(data=data, node=node)
  return data


async def handle_neither_node_being_none(data: Data) -> Data:
  if data.current_nodes.one.value <= data.current_nodes.two.value:
    data = await handle_node_two_being_none(data)
    return data
  if data.current_nodes.two.value < data.current_nodes.one.value:
    data = await handle_node_one_being_none(data)
    return data


TYPE_SWITCHER = {
  '.': handle_neither_node_being_none,
  'none.': handle_node_one_being_none,
  '.none': handle_node_two_being_none,
  'none.none': handle_both_nodes_being_none,
}


async def merge_sorted_linked_lists(data: Data) -> Data:
  while not data.exit_loop:
    cases = [
      int(data.current_nodes.one is None) * 'none',
      int(data.current_nodes.two is None) * 'none',
    ]
    cases = '.'.join(cases)
    switcher = TYPE_SWITCHER[cases]
    data = await switcher(data=data)
  return data


async def get_merged_list(data: Data) -> Data:
  data.linked_lists.merged.head = data.linked_lists.merged.head.next_node
  # Convert linked list to list
  data.merged_list = await algorithms_linked_list.main(
    linked_list=data.linked_lists.merged)
  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      merged: {data.merged_list} 
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data = await get_linked_lists(data=data)
  data = await set_current_nodes(data=data)
  data = await merge_sorted_linked_lists(data=data)
  data = await get_merged_list(data=data)
  data = await get_response(data=data)
  return data

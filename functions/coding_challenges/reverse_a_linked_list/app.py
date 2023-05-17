#!usr/bin/env python3

from typing import Any, List
from dataclasses import dataclass, asdict
import yaml

from api import models
from functions.algorithms.linked_list import app as linked_list_algorithms
from functions.algorithms.linked_list.app import LinkedList, Node


@dataclass
class Body(models.Body):
  items: List[Any] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
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



async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      reversed_items: {data.reversed_items}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data.linked_list = await linked_list_algorithms.main(
    values=data.body.items)
  data.linked_list = await reverse_linked_list(linked_list=data.linked_list)
  data.reversed_items = await linked_list_algorithms.main(
    linked_list=data.linked_list)
  data = await get_response(data=data)
  return data

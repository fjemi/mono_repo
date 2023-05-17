#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from copy import deepcopy
from typing import List, Any
import yaml

from api import models
from functions.algorithms.linked_list import app as linked_list_algorithms
from functions.algorithms.linked_list.app import Node, LinkedList


@dataclass 
class Body(models.Body):
  k: int = 0
  head: List[int] | None = None


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None


@dataclass
class ModuleData:
  body: Body | None = None
  linked_list: LinkedList | None = None
  current_node: Node | None = None
  node_groups: List[List[Node]] = field(
    default_factory=lambda: [])
  modified_linked_list: LinkedList | None = None
  output: List[Any] | None = None


@dataclass
class Store:
  node_group: List[Node] | None = None
  current_node: Node | None = None


async def get_node_group_and_current_node(
  current_node: LinkedList,
  k: int,
) -> List[Node] | None:
  store = Store(
    node_group=[],
    current_node=deepcopy(current_node),
  )

  for i in range(k):
    _ = i
    if store.current_node is None:
      break

    node = Node(value=store.current_node.value)
    store.node_group.append(node)
    store.current_node = store.current_node.next_node

  n = len(store.node_group)
  if n != k or n == 0:
    store.node_group = []
    store.current_node = current_node

  return store


async def get_node_groups(data: ModuleData) -> ModuleData:
  while [] not in data.node_groups:
    store = await get_node_group_and_current_node(
      current_node=data.current_node,
      k=data.body.k,
    )
    data.node_groups.append(store.node_group)
    data.current_node = store.current_node
  return data


async def process_node_groups(
  node_groups: List[List[Node | None]],
  current_node: Node | None,
) -> LinkedList:
  store = []

  m = len(node_groups)
  for i in range(m):
    n = len(node_groups[i])
    # Handle groups with a single node
    if n == 1:
      store.append(node_groups[i][0])
      continue
    # Handle groups with multiple nodes
    for j in range(1, n):
      node_groups[i][j].next_node = node_groups[i][j - 1]
      if j != n - 1:
        continue
      store.append(node_groups[i][j])

  store = [current_node] + store
  return store


async def get_modified_linked_list(
  node_groups: List[List[Node | None]],
  k: int,
) -> LinkedList:
  _ = k
  store = LinkedList()
  # Original linked list is empty
  if node_groups in [[None], []]:
    return store

  # Reverse the order of the first to nth
  # groups of nodes to get the nodes in
  # reverse k order
  temp = node_groups[1:]
  temp.reverse()
  node_groups = [node_groups[0]] + temp

  # Form the linked list from the groups of nodes
  n = len(node_groups)
  for i in range(1, n):
    current_node = node_groups[i]
    # Set the next node for the last node in the
    # group, to the first node in the preceding group
    while True:
      if current_node.next_node is None:
        current_node.next_node = node_groups[i - 1]
        break
      if current_node.next_node is not None:
        current_node = current_node.next_node
  # Last node group is the full modified linked list
  store.head = node_groups[-1]
  return store


async def get_response(data: ModuleData) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      reversed_nodes: {data.output}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = ModuleData(body=request.data.body)
  request = None
  data.linked_list = await linked_list_algorithms.main(
    values=data.body.head)
  data.current_node = data.linked_list.head
  data = await get_node_groups(data=data)
  data.node_groups = await process_node_groups(
    node_groups=data.node_groups,
    current_node=data.current_node,
  )
  data.modified_linked_list = await get_modified_linked_list(
    node_groups=data.node_groups,
    k=data.body.k,
  )
  data.output = await linked_list_algorithms.main(
    linked_list=data.modified_linked_list)
  data = await get_response(data=data)
  return data

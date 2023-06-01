#!/usr/bin/env python3

from __future__ import annotations
import dataclasses as dc
from typing import Any, List
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Node:
  value: Any | None = None
  left: Node | None = None
  right: Node | None = None


@dc.dataclass
class Tree:
  root: Node | None = None


@dc.dataclass
class Body:
  tree: dict | Tree | None = None
  array: List[Any] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  call_method: str = 'module'
  result: Tree | dict | list | None = None


@dc.dataclass
class Indices:
  left: int = 0
  right: int = 0


async def get_empty_tree(*args, **kwargs) -> Tree:
  _ = args, kwargs
  tree = Tree()
  return tree


async def get_list_of_nodes(array: List[Any]) -> List[Node]:
  nodes = []
  n = len(array)
  for i in range(n):
    value = array[i]
    node = Node(value=value)
    nodes.append(node)
  return nodes


# TODO: implement switcher
# NODES_SWITCHER = {
#   'left.right': ,
#   'left.': ,
#   '.right': ,
#   '.': ,
# }


async def connect_nodes_to_form_tree(nodes: List[Node]) -> List[Node]:
  indices = Indices()

  n = len(nodes)
  for i in range(n):
    node = nodes[i]

    indices.left = 2 * i + 1
    indices.right = indices.left + 1

    cases = [
      int(indices.left < n) * 'left',
      int(indices.right < n) * 'right',
    ]
    cases = '.'.join(cases)

    if cases == 'left.right':
      node.right = nodes[indices.right]
      node.left = nodes[indices.left]
      continue

    if cases == '.right':
      node.right = nodes[indices.right]
      continue

    if cases == 'left.':
      node.left = nodes[indices.left]
      continue

    if cases == '.':
      break

  return nodes


async def get_tree(array: List[Any]) -> Tree:
  nodes = await get_list_of_nodes(array=array)
  nodes = await connect_nodes_to_form_tree(nodes=nodes)
  tree = Tree(root=nodes[0])
  return tree


ARRAY_LENGTH_SWITCHER = {
  'zero': get_empty_tree,
  'non_zero': get_tree,
}


async def convert_array_to_tree(data: Data) -> Data:
  n = len(data.body.array)
  cases = 'zero' if n == 0 else 'non_zero'
  switcher = ARRAY_LENGTH_SWITCHER[cases]
  data.result = await switcher(array=data.body.array)
  return data


async def convert_tree_to_array(data: Data) -> Data:
  store = []

  data.result = store
  return data


CONVERSION_HANDLER = {
  'array': convert_array_to_tree,
  'tree': convert_tree_to_array,
}


async def get_response(data: Data) -> Tree | dict | list:
  if data.call_method == 'module':
    return data.result
  if data.body.array is not None:
    data = {'tree': dc.asdict(data.result)}
  elif data.body.tree is not None:
    data = {'array': data.result}
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  array: List[Any] | None = None,
  tree: Tree | None = None,
) -> Tree | List[Any] | None:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={
      'body': Body,
    },
    main_data_class=Data,
  )
  object_type = 'array' if data.body.tree is None else 'tree'
  handler = CONVERSION_HANDLER[object_type]
  data = await handler(data=data)
  data = await get_response(data=data)
  return data

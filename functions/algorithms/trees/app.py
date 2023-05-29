#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, fields, asdict
from typing import Any, List

from api import models as api_models


@dataclass
class Node:
  value: Any | None = None
  left: Node | None = None
  right: Node | None = None


@dataclass
class Tree:
  root: Node | None = None


@dataclass
class Body:
  tree: dict | Tree | None = None
  array: List[Any] | None = None


@dataclass
class Data:
  body: Body | None = None
  array_n: int = 0
  call_method: str = 'module'
  result: Tree | dict | list | None = None


@dataclass
class Indices:
  left: int = 0
  right: int = 0


async def process_call_from_api(
  data: Data,
  _locals: dict
) -> Data:
  body = Body()
  request = _locals['request']

  for attribute in fields(body):
    if not hasattr(request.data.body, attribute.name):
      continue
    value = getattr(request.data.body, attribute.name)
    if value is None:
      continue
    setattr(body, attribute.name, value)

  data.body = body
  return data


async def process_call_from_module(
  data: Data,
  _locals: dict,
) -> Data:
  del _locals['request']
  body = Body(**_locals)
  data.body = body
  return data


PROCESS_MAIN_ARGUMENTS = {
  'api': process_call_from_api,
  'module': process_call_from_module,
}


async def process_main_arguments(_locals: dict) -> Data:
  data = Data()
  data.call_method = 'api' if _locals['request'] else 'module'
  switcher = PROCESS_MAIN_ARGUMENTS[data.call_method]
  data = await switcher(data=data, _locals=_locals)
  return data


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
    data = {'tree': asdict(data.result)}
  elif data.body.tree is not None:
    data = {'array': data.result}
  return data


# pylint: disable=unused-argument
async def main(
  request: api_models.Request | None = None,
  array: List[Any] | None = None,
  tree: Tree | None = None,
) -> Tree | List[Any] | None:
  data = await process_main_arguments(_locals=locals())
  object_type = 'array' if data.body.tree is None else 'tree'
  handler = CONVERSION_HANDLER[object_type]
  data = await handler(data=data)
  data = await get_response(data=data)
  return data

#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List


@dataclass
class Node:
  value: Any | None = None
  left: Node | None = None
  right: Node | None = None


@dataclass
class Tree:
  root: Node | None = None


@dataclass
class Data:
  array: List[str] | None = None
  array_n: int = 0
  tree: Tree | None = None


@dataclass
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


async def convert_array_to_tree(_locals: dict) -> Tree:
  array = _locals['array']
  n = len(array)
  cases = [
    int(n == 0) * 'zero',
    int(n >= 1) * 'non_zero',
  ]
  cases = ''.join(cases)
  switcher = ARRAY_LENGTH_SWITCHER[cases]
  tree = await switcher(array=array)
  return tree


async def convert_tree_to_array(_locals: dict) -> List[Any]:
  tree = _locals['tree']
  store = [tree.root.value]
  # TODO: Implement this

  return store


async def return_none(*args, **kwargs) -> None:
  _ = args, kwargs
  return None


ARGUMENTS_SWITCHER = {
  'array': convert_array_to_tree,
  'tree': convert_tree_to_array,
  '': return_none,
}


async def main(
  array: List[Any] | None = None,
  tree: Tree | None = None,
) -> Tree | List[Any] | None:
  cases = [
    int(array is not None) * 'array',
    int(tree is not None) * 'tree',
  ]
  cases = ''.join(cases)
  switcher = ARGUMENTS_SWITCHER[cases]
  result = await switcher(_locals=locals())
  return result

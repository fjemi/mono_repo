#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Any
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments
from functions.algorithms.trees import app as shared_tree
from functions.algorithms.trees.app import Tree


@dc.dataclass
class Body:
  root: List[Any] | None = None


@dc.dataclass
class Branches:
  left: List[Any] | None = None
  right: List[Any] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  tree: Tree | None = None
  output: bool = False


async def check_if_symmetric_tree(data: Data) -> Data:
  tree = await shared_tree.main(array=data.body.root)
  left = str(tree.root.left)
  right = str(tree.root.right)

  data.output = False
  if right == left:
    data.output = True

  return data


async def get_response(data: Data) -> dict:
  return {'output': data.output}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  root: List[Any] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await check_if_symmetric_tree(data=data)
  data = await get_response(data=data)
  return data

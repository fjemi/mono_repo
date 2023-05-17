#!/usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import yaml

from api import models
from shared.tree import app as shared_tree
from shared.tree.app import Tree


@dataclass
class Body(models.Body):
  root: List[Any] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Branches:
  left: List[Any] | None = None
  right: List[Any] | None = None


@dataclass
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
  print(tree.root.left, tree.root.right, sep='\n\n')

  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: {data.output}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> Data:
  data = Data(body=request.data.body)
  request = None
  data = await check_if_symmetric_tree(data=data)
  data = await get_response(data=data)
  return data

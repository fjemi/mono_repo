#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List
import yaml

from api import models


@dataclass
class Body(models.Body):
  root: List[int | None] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  bst_check: bool = False
  root_n: int = 0
  node_indices: List[List[int]] | None = None
  node_keys: List[List[int]] | None = None


async def get_node_indices(
  root_n: int,
) -> List[List[int]]:
  store = [[0, 1, 2]]
  root_range = range(1, root_n)
  for i in root_range:
    indices = [
      i,
      2 * i + 1,
      2 * i + 2,
    ]
    store.append(indices)
  return store


async def get_node_keys(
  node_indices: List[int],
  root: List[int],
  root_n: int,
) -> List[List[int]]:
  keys = []
  for indices in node_indices:
    store = []
    for index in indices:
      key = None
      if index < root_n:
        key = root[index]
      store.append(key)
    keys.append(store)
  return keys


async def case_parent_left_not_none_and_right_none(
  parent: int,
  left: int,
  right: None,
) -> bool:
  _ = right
  return parent > left


async def case_parent_right_not_none_and_left_none(
  parent: int,
  left: None,
  right: int,
) -> bool:
  _ = left
  return parent < right


async def case_parent_left_and_right_not_none(
  parent: int,
  left: int,
  right: int,
) -> bool:
  conditions = [
    left < parent,
    right > parent,
  ]
  conditions = sum(conditions) / len(conditions) == 1
  return conditions


async def case_parent_none_and_left_or_right_not_none(
  parent: None,
  left: int,
  right: int,
) -> bool:
  _ = parent, left, right
  return False


async def case_parent_left_right_are_none(
  parent: None,
  left: None,
  right: None,
) -> bool:
  _ = parent, left, right
  return True


async def case_parent_not_none_and_left_and_right_none(
  parent: int,
  left: None,
  right: None,
) -> bool:
  _ = parent, left, right
  return True


SWITCHER = {
  '1.1.1': case_parent_left_right_are_none,
  '1.1.0': case_parent_none_and_left_or_right_not_none,
  '1.0.1': case_parent_none_and_left_or_right_not_none,
  '0.1.1': case_parent_not_none_and_left_and_right_none,
  '1.0.0': case_parent_none_and_left_or_right_not_none,
  '0.1.0': case_parent_right_not_none_and_left_none,
  '0.0.1': case_parent_left_not_none_and_right_none,
  '0.0.0': case_parent_left_and_right_not_none,
}


async def check_if_root_is_bst(
  node_keys: List[List[int]],
) -> bool:
  for keys in node_keys:
    parent = keys[0]
    left = keys[1]
    right = keys[2]

    _case = [
      str(int(parent is None)),
      str(int(left is None)),
      str(int(right is None)),
    ]
    _case = '.'.join(_case)
    function = SWITCHER[_case]
    result = await function(
      parent=parent,
      left=left,
      right=right,
    )
    if result is False:
      return False
  return True


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      is_bst: {data.bst_check}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data.root_n = len(data.body.root)
  data.node_indices = await get_node_indices(root_n=data.root_n)
  data.node_keys = await get_node_keys(
    node_indices=data.node_indices,
    root=data.body.root,
    root_n=data.root_n,
  )
  data.bst_check = await check_if_root_is_bst(node_keys=data.node_keys)
  data = await get_response(data=data)
  return data

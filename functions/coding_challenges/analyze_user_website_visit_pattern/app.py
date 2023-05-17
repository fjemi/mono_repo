#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import yaml

from api import models


@dataclass
class Body(models.Body):
  websites: List[str] | None = None
  usernames: List[str] | None = None
  timestamps: List[int] | None = None


@dataclass
class Data(models.Data):
  body: Body = field(default_factory=lambda: Body())


@dataclass
class Request(models.Request): 
  data: Data = field(default_factory=lambda: Data())


@dataclass
class Data:
  body: Body | None = None
  sequence_n: int = 3
  aggregated_data: Dict[str, List[str]] | None = None
  combinations: List[str] | Dict[str, int] | None = None


async def get_aggregated_data(data: Data) -> Data:
  store = {}
  websites_n = len(data.body.websites)
  # Number of zeros to pad timestamp integers with
  zero_fill_n = len(str(websites_n))

  for i in range(websites_n):
    username = data.body.usernames[i]
    if username not in store:
      store[username] = []

    # Pad timestamps with zeros
    timestamp = data.body.timestamps[i]
    timestamp = str(timestamp).zfill(zero_fill_n)
    # Combine timestamp and website into a string
    website = f'{timestamp}_{data.body.websites[i]}'
    store[username].append(website)
  data.aggregated_data = store
  return data


async def get_next_branches(
  previous_branches: List[str],
  leaves: List[str | int],
) -> str:
  store = []
  for previous_branch in previous_branches:
    previous_leaf = previous_branch.split('.')[-1]
    previous_leaf = int(previous_leaf)
    for leaf in leaves:
      leaf = int(leaf)
      if leaf >= previous_leaf:
        continue
      next_branch = f'{previous_branch}.{leaf}'
      store.append(next_branch)
  return store


async def get_combinations(
  websites: List[str],
  sequence_n: int,
):
  websites_n = len(websites)
  if websites_n < sequence_n:
    return []

  leaves = [str(i) for i in range(websites_n)]
  # Set tree root
  tree = [leaves]
  # Add branches to the tree
  count = 0
  while count < sequence_n - 1:
    previous_branches = tree[-1]
    next_branches = await get_next_branches(
      previous_branches=previous_branches,
      leaves=leaves,
    )
    tree.append(next_branches)
    count += 1

  return tree[-1]


async def convert_indices_to_websites(
  combination: str,
  websites: List[str]
) -> List[str]:
  store = ''
  indices = combination.split('.')
  indices.sort()
  for i in indices:
    i = int(i)
    website = websites[i]
    website = website.split('_')[1]
    store = f'{store}.{website}'

  return store[1:]


async def process_combinations(
  combinations: List[str],
  websites: List[str],
) -> List[str]:
  store = []
  for combination in combinations:
    combination = await convert_indices_to_websites(
      combination=combination,
      websites=websites,
    )
    store.append(combination)
  return store


async def get_combinations_from_aggregrated_data(data: Data) -> Data:
  store = {}
  for user, websites in data.aggregated_data.items():
    combinations = await get_combinations(
      websites=websites,
      sequence_n=data.sequence_n,
    )
    combinations = await process_combinations(
      combinations=combinations,
      websites=websites,
    )
    store[user] = combinations

  data.combinations = store
  return data


async def merge_username_combinations(data: Data) -> Data:
  store = []
  values = list(data.combinations.values())
  for value in values:
    store.extend(value)
  data.combinations = store
  return data


async def get_combination_counts(data: Data) -> Data:
  store = {}
  combinations_n = len(data.combinations)
  for i in range(combinations_n):
    if data.combinations[i] not in store:
      store[data.combinations[i]] = 0
    store[data.combinations[i]] += 1
  data.combinations = store
  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output:
      3_sequence: {list(data.combinations.keys())[0]}
      visits: {list(data.combinations.values())[0]}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data = await get_aggregated_data(data=data)
  data = await get_combinations_from_aggregrated_data(data=data)
  data = await merge_username_combinations(data=data)
  data = await get_combination_counts(data=data)
  data = await get_response(data=data)
  return data

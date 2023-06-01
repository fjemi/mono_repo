#!usr/bin/env python3

import dataclasses as dc
from typing import List, Dict, Any
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  players: List[Dict[str, int]] | Dict[str, int] | None = None


@dc.dataclass
class Player:
  name: List[str] | None = None
  score: List[int] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  players_by_scores: Dict[int, List[str]] | None = None
  sorted_players: List[Player] = dc.field(default_factory=lambda: [])


async def aggregate_player_scores(data: Data) -> Data:
  store = {}
  for item in data.body.players:
    name = item['name']
    if name in store:
      store[name] += item['score']
    else:
      store[name] = item['score']

  data.body.players = store
  return data


async def get_players_by_score(data: Data) -> Data:
  store = {}

  for player, score in data.body.players.items():
    if score not in store:
      store[score] = []
    store[score].append(player)
    store[score].sort()

  data.players_by_scores = store
  return data


async def sort_players_by_scores_and_alphabetically(data: Data) -> Data:
  store = []
  scores = data.players_by_scores.keys()
  for score in reversed(scores):
    for name in data.players_by_scores[score]:
      store.append(dict(name=name, score=score))
  data.sorted_players = store
  return data


async def get_response(data: Data) -> dict:
  return {'players': data.sorted_players}



# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  players: List[Dict[str, int]] | Dict[str, int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await aggregate_player_scores(data=data)
  data = await get_players_by_score(data=data)
  data = await sort_players_by_scores_and_alphabetically(data=data)
  data = await get_response(data=data)
  return data

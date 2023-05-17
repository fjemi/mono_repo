#!usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List, Union, Dict, Any
import yaml

from api import models


@dataclass
class Body(models.Body):
  players: List[Dict[str, int]] | Dict[str, int] | None = None


@dataclass
class Data(models.Data):
  body: Body = field(default_factory=lambda: Body())


@dataclass
class Request(models.Request):
  data: Data = field(default_factory=lambda: Data())


@dataclass
class Player:
  name: List[str] | None = None
  score: List[int] | None = None


@dataclass
class Props:
  body: Body | None = None
  players_by_scores: Dict[int, List[str]] | None = None
  sorted_players: List[Player] = field(default_factory=lambda: [])


async def aggregate_player_scores(props: Props) -> Props:
  store = {}
  for item in props.body.players:
    name = item['name']
    if name in store:
      store[name] += item['score']
    else:
      store[name] = item['score']

  props.body.players = store
  return props


async def get_players_by_score(props: Props) -> Props:
  store = {}

  for player, score in props.body.players.items():
    if score not in store:
      store[score] = []
    store[score].append(player)
    store[score].sort()

  props.players_by_scores = store
  return props


async def sort_players_by_scores_and_alphabetically(props: Props) -> Props:
  store = []
  scores = props.players_by_scores.keys()
  for score in reversed(scores):
    for name in props.players_by_scores[score]:
      store.append(dict(name=name, score=score))
  props.sorted_players = store
  return props


async def get_response(props: Props) -> models.Response:
  props = f'''
    input: {asdict(props.body)} 
    output: 
      players: {props.sorted_players}
  '''
  props = yaml.safe_load(props)
  props = models.Response(data=props)
  return props


async def main(request: Request) -> models.Response:
  props = Props(body=request.data.body)
  request = None
  props = await aggregate_player_scores(props=props)
  props = await get_players_by_score(props=props)
  props = await sort_players_by_scores_and_alphabetically(props=props)
  props = await get_response(props=props)
  return props

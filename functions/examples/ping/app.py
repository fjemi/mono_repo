#! /usr/bin/python3

from dataclasses import dataclass, field


@dataclass
class Data:
  ping: str = 'pong'


@dataclass
class Response:
  code: int = 200
  status: str = 'OK'
  data: dict = field(default_factory=lambda: {'ping': 'pong'})
  

async def main(*arg, **kwargs) -> Response:
  response = Response()
  return response

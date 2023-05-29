#! /usr/bin/python3

from dataclasses import dataclass, asdict


@dataclass
class Data:
  ping: str = 'pong'


async def main(*args, **kwargs) -> dict:
  _ = args, kwargs
  data = Data()
  data = asdict(data)
  return data

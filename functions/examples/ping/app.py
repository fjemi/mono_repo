#! /usr/bin/python3

import dataclasses as dc


@dc.dataclass
class Data:
  ping: str = 'pong'


async def main(*args, **kwargs) -> dict:
  _ = args, kwargs
  data = Data()
  data = dc.asdict(data)
  return data

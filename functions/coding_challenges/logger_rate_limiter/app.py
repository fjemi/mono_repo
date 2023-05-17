#!/usr/bin/env python3

from typing import List, Dict
from dataclasses import dataclass, field, asdict
import yaml

from api import models


@dataclass
class Body(models.Body):
  logs: List[List[str | int]] | None = None
  time_s: int = 10


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  stored: Dict[str, List[int]] = field(default_factory=lambda: {})
  printed: Dict[str, List[int]] = field(default_factory=lambda: {})
  count: int = 0


async def message_never_printed(
  printed: dict,
  message: str,
  timestamp: str,
  time_s: int,
) -> dict:
  _ = time_s
  printed[message] = [timestamp]
  return printed


async def message_previously_printed(
  printed: dict,
  message: str,
  timestamp: str,
  time_s: int,
) -> dict:
  previous_timestamp = printed[message][-1]
  difference = abs(previous_timestamp - timestamp)
  if difference < time_s:
    return printed
  printed[message].append(timestamp)
  return printed


SWITCHER = {
  'never_printed': message_never_printed,
  'previously_printed': message_previously_printed,
}


async def get_messages_to_print(data: Data) -> Data:
  printed = {}
  for log in data.body.logs:
    timestamp, message = log

    _case = 'never_printed'
    if message in printed:
      _case = 'previously_printed'
    switcher = SWITCHER[_case]
    printed = await switcher(
      message=message,
      timestamp=timestamp,
       printed=printed,
       time_s=data.body.time_s,
    )

  data.printed = printed
  return data


async def count_printed(printed: dict) -> int:
  count = 0
  values = list(printed.values())
  for value in values:
    count += len(value)
  return count


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
      printed_messages:
        values: {data.printed}
        n: {data.count}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  body = Body(**asdict(request.data.body))
  data = Data(body=body)
  request = None
  data = await get_messages_to_print(data=data)
  data.count = await count_printed(printed=data.printed)
  data = await get_response(data=data)
  return data

#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from typing import List, Dict
import requests
import bs4
import yaml

from api import models
from shared.load_function_from_path import app as load_function_from_path
from shared.get_environment import app as get_environment


@dataclass
class Body(models.Body):
  sites: List[str] | None = None


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Data:
  body: Body | None = None
  html: str | None = None


async def get_url(data: Data) -> Data:
  return data


async def get_html(data: Data) -> Data:
  url = 'http://www.usasexguide.nl/forum/archive/index.php?s=0cf6fc9f10a150e45cd2b23519cdec10&api=1'
  response = requests.get(url)
  if response.status_code != 200:
    raise RuntimeError()
  data.html = response.content
  return data


async def process_html():
  ...


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)}
    output: 
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  body = Body(**asdict(request.data.body))
  data = Data(body=body)
  request = None

  data = await get_html(data=data)
  

  print(data)
  data = await get_response(data=data)
  return data

#!/usr/bin/env python3

import dataclasses as dc
from typing import List, Dict
import requests
import bs4
import yaml
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments
from shared.load_function_from_path import app as load_function_from_path
from shared.get_environment import app as get_environment


@dc.dataclass
class Body:
  sites: List[str] | None = None


@dc.dataclass
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


async def get_response(data: Data) -> dict:
  return


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  sites: str | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None

  data = await get_html(data=data)


  print(data)
  data = await get_response(data=data)
  return data

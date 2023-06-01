#!/usr/bin/env python3

import dataclasses as dc
from typing import Any
import os
import html
import yaml
from fastapi import HTTPException, Request

from functions.wrappers.aws import app as aws_wrapper
from shared.format_main_arguments import app as format_main_arguments


THIS_MODULE_DIRECTORY = os.path.dirname(__file__)


@dc.dataclass
class Body:
  database: str | None = None
  query: str | None = None
  parameters: Any | None = None
  text: str | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  module_directory: str = THIS_MODULE_DIRECTORY
  call_method: str =  'module'
  result: Any | None = None


async def get_query_from_path(data: Data) -> Data:
  if data.body.text:
    return data

  file_name = f'{data.body.database}.yml'
  path = os.path.join(
    data.module_directory,
    'queries',
    file_name,
  )
  if not os.path.exists(path):
    raise HTTPException(
    status_code=404,
    detail=f'{data.body.database} does not exist',
  )

  queries = {}
  with open(
    file=path,
    mode='r',
    encoding='utf-8',
  ) as file:
    queries = yaml.safe_load(file)
  if data.body.query not in queries:
    detail = f'{data.body.query} does not exist for {data.body.database}'
    raise HTTPException(
      status_code=404,
      detail=detail,
    )
  data.body.text = queries[data.body.query]
  return data


async def sanitize_query_text(data: Data) -> Data:
  if data.body.database in ['dynamodb']:
    return data
  data.body.text = html.escape(data.body.text)
  return data


async def format_query_text(data: Data) -> Data:
  data.body.text = os.path.expandvars(data.body.text)

  if not data.body.parameters:
    return data

  for key, value in data.body.parameters.items():
    data.body.text = data.body.text.replace(f'[{key}]', str(value))
  return data


async def query_dynamodb_database(data: Data) -> Data:
  service = yaml.safe_load(data.body.text)
  data.result = await aws_wrapper.main(service=service)
  return data


DATABASES = {
  'dynamodb': query_dynamodb_database,
}


async def process_query(data: Data) -> Data:
  switcher = DATABASES[data.body.database]
  data = await switcher(data=data)
  return data


async def get_response(data: Data) -> Any:
  return data.result


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  database: str | None = None,
  query: str | None = None,
  parameters: Any | None = None,
  text: str | None = None,
) -> Any:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  data = await get_query_from_path(data=data)
  data = await sanitize_query_text(data=data)
  data = await format_query_text(data=data)
  data = await process_query(data=data)
  data = await get_response(data=data)
  return data


async def example() -> None:
  database = 'dynamodb'
  text = '''
    client: dynamodb
    method: list_tables
    parse_response:
    - TableNames
  '''
  result = await main(
    database=database,
    text=text,
  )
  print(result.data)


if __name__ == '__main__':
  import asyncio


  asyncio.run(example())

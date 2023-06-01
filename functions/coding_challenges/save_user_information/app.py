#!/usr/bin/env python3

import dataclasses as dc
from typing import Any
import time
import os
import json
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from shared.format_main_arguments import app as format_main_arguments
from functions.wrappers.aws import app as asw_wrapper
from shared.get_environment import app as get_environment


THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)


@dc.dataclass
class Body:
  name: str | None = None
  age: int | float | None = None
  username: str | None = None
  save_to: str = 's3'


@dc.dataclass
class Form:
  name: str | None = None
  age: int | float | None = None
  username: str | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  form: Form | None = None
  request_method: str = 'GET'
  json: str | None = None
  folder: str | None = None
  timestamp: int | None = None
  response: Any | None = None


async def handle_get_request(data: Data) -> Data:
  _ = data
  directory = os.path.dirname(THIS_MODULE_PATH)
  directory = os.path.join(directory, 'static')
  template = Jinja2Templates(
    directory=directory,
    auto_reload=ENV.API_RELOAD,
  )

  template = template.TemplateResponse(
    'index.html',
    context={'request': {}},
  )
  return template


async def format_form_data(data: Data) -> Data:
  if data.body:
    return data

  for field in dc.fields(data.form):
    value = getattr(data.form, field.name)
    print(value)
    # value = value.decode('utf-8')

  data.form = dc.asdict(data.form)
  data.body = Body(**data.form)
  data.form = None
  return data


async def get_folder_name(this_module_path: str) -> str:
  directory = os.path.dirname(this_module_path)
  directory = directory.split(os.sep)
  folder = directory[-1]
  return folder


async def save_to_s3(data: Data) -> Data:
  key = f'{data.folder}/{data.body.username}.{data.body.name}.{data.body.age}'

  response = None

  try:
    service = f'''
      client: s3
      method: get_object
      parameters:
        Bucket: {ENV.S3_BUCKET}
        Key: {key}
      parse_response:
      - ResponseMetadata.HTTPStatusCode
    '''
    response = await asw_wrapper.main(service=service)
  except Exception:
    pass
  if response == [200]:
    raise HTTPException(
      status_code=409,
      detail='User information has already been submitted',
    )

  service = f'''
    client: s3
    method: put_object
    parameters:
      Bucket: {ENV.S3_BUCKET}
      Body: '{data.json}'
      Key: {key}
    parse_response:
    - ResponseMetadata.HTTPStatusCode
  '''

  response = await asw_wrapper.main(service=service)
  if response != [{'ResponseMetadata.HTTPStatusCode': 200}]:
    raise HTTPException(
      status_code=500,
      detail=f'Could not save {key} to S3',
    )

  data.response = {
    'bucket': ENV.S3_BUCKET,
    'key': key,
  }
  return data


async def save_to_file_system(data: Data) -> Data:
  directory_path = os.path.join(
    ENV.DATA_PATH,
    data.folder,
  )

  if not os.path.exists(directory_path):
    os.makedirs(directory_path)

  file_path = os.path.join(
    directory_path,
    f'{data.body.username}.{data.body.name}.{data.body.age}.json',
  )

  if os.path.exists(file_path):
    raise HTTPException(
      status_code=409,
      detail='User information has already been submitted',
    )

  with open(
    file=file_path,
    mode='w',
    encoding='utf-8',
  ) as file:
    file.write(data.json)

  data.response = {'path': file_path}
  return data


SAVE_TO = {
  's3': save_to_s3,
  'file_system': save_to_file_system,
}


async def save_post_request_parameters(data: Data) -> Data:
  data.folder = await get_folder_name(this_module_path=THIS_MODULE_PATH)
  function = SAVE_TO[data.body.save_to]
  data = await function(data=data)
  return data


async def handle_post_request(data: Data) -> Data:
  data = await format_form_data(data=data)

  data.request_method = 'POST'
  data.timestamp = int(time.time())
  data.json = dc.asdict(data.body)
  del data.json['save_to']
  data.json = json.dumps(data.json)

  data = await save_post_request_parameters(data=data)
  return data


REQUEST_HANDLER = {
  'GET': handle_get_request,
  'POST': handle_post_request,
}


async def get_response(data: Data) -> JSONResponse | Jinja2Templates:
  if isinstance(data, Data):
    data = JSONResponse(
      status_code=200,
      content=data.response,
    )
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  name: str | None = None,
  age: int | float | None = None,
  username: str | None = None,
  save_to: str | None = None,
) -> dict | Jinja2Templates:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body, 'form': Form},
    main_data_class=Data,
  )
  # return
  handler = REQUEST_HANDLER[request.method]
  request = None
  data = await handler(data=data)
  data = await get_response(data=data)
  return data

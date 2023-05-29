#!/usr/bin/env python3

from typing import List, Any, Callable
from dataclasses import make_dataclass, field, asdict, is_dataclass
import pathlib
import time
import yaml
from fastapi import (
  FastAPI,
  Request,
  Response,
)
import uvicorn
from requests_toolbelt.multipart.decoder import MultipartDecoder

import models
from shared.get_environment import app as get_environment
from shared.load_function_from_path import app as load_function_from_path
from api.openapi import app as openapi


THIS_MODULE_PATH = __file__
ENV = get_environment.main({'module_path': THIS_MODULE_PATH})


app = FastAPI()

# Set the OpenAPI schema for the app
openapi_schema = openapi.main(app_module_path=THIS_MODULE_PATH)
app.openapi_schema = openapi_schema.schema
ROUTES = openapi_schema.routes


async def create_dataclass(dictionary: dict, name: str):
  dataclass_fields = []
  for key, value in dictionary.items():
    key = key.replace('-', '_').lower()
    dataclass_field = [key, Any, field(default_factory=lambda: value)]
    dataclass_fields.append(dataclass_field)
  data_class = make_dataclass(name, dataclass_fields)
  return data_class()


# TODO: Consider formatting request attributes at the function level
async def format_request_headers(request: Request) -> Request:
  store = []
  for key, value in request.headers.items():
    key = key.replace('-', '_').lower()
    store.append([
      key,
      str,
      value,
    ])
  headers = make_dataclass(
    'Headers', 
    store,
    slots=True,
  )
  request.data.headers = headers()
  # request._headers = None
  del request._headers
  return request


async def format_query_params(request: Request) -> Request:
  dictionary = {}
  if request.query_params is not None:
    dictionary = request.query_params._dict
  request.data.query_params = await create_dataclass(
    dictionary=dictionary,
    name='QueryParams',
  )
  request._query_params = None
  return request


async def format_path_params(request: Request) -> Request:
  dictionary = {}
  if request.path_params:
    dictionary = request.path_params
  request.data.path_params = await create_dataclass(
    dictionary=dictionary,
    name='PathParams',
  )
  request._path_params = None
  return request


async def get_request_handler(request: Request) -> Request:
  request = await format_query_params(request=request)
  return request


async def handle_application_json(request: Request) -> Request:
  body = await request.json()
  request.data.body = await create_dataclass(
    dictionary=body,
    name='Body',
  )
  request._json = None
  return request


async def handle_text_plain(request: Request) -> Request:
  body = await request.body()
  body = yaml.safe_load(body)

  store = []
  for key, value in body.items():
    value_type = type(value).__name__
    type_hint = f'{value_type} | None'
    _field = [
      key,
      type_hint,
      None,
    ]
    store.append(_field)

  Body = make_dataclass(
    'Body',
    store,
    slots=True,
  )
  request.data.body = Body(**body)
  request._body = None
  return request


async def convert_headers_attributes_to_dictionaries(
  values: List[str],
) -> dict:
  if not isinstance(values, list):
    return values

  values_n = reversed(range(len(values)))
  store = {}
  for i in values_n:
    if values[i] == 'form-data':
      del values[i]
    values[i] = values[i].replace('"', '').strip()
    key, value = values[i].split('=')
    store[key] = value
  return store


async def format_multipart_headers(headers: Any) -> dict:
  store = {}
  for key in headers:
    value = headers[key]

    key = key.decode('utf-8')
    key = key.lower().replace('-', '_')
    values = value.decode('utf-8').split(';')

    if key != 'content_type':
      store[key] = await convert_headers_attributes_to_dictionaries(
        values=values)
      continue
    if key == 'content_type':
      store[key] = values[0]
      continue
  return store


async def handle_multipart_form_data(request: Request) -> Request:
  content = await request.body()
  decoder = MultipartDecoder(
    content=content,
    content_type=request.data.headers.content_type,
  )

  store = {}
  for part in decoder.parts:
    headers = await format_multipart_headers(
      headers=part.headers)
    part_name = headers['content_disposition']['name']
    store[part_name] = part.content
  request.data.form = store
  return request


CONTENT_HANDLER = {
  'application/json': handle_application_json,
  'text/plain': handle_text_plain,
  # 'text/plain;charset=UTF-8': handle_text_plain,
  'multipart/form-data': handle_multipart_form_data,
}


async def post_request_handler(request: Request) -> Request:
  content_type = request.data.headers.content_type
  content_type = content_type.split(';')[0]
  content_handler = CONTENT_HANDLER[content_type]
  request = await content_handler(request=request)
  return request


REQUEST_HANDLER = {
  'GET': get_request_handler,
  'POST': post_request_handler,
}


async def post_response_handler(
  response: Any,
  request: Request,
) -> Any:
  media_type = 'text/plain'
  if request.data.headers.content_type == media_type:
    if is_dataclass(response):
      response = asdict(response)
    content = yaml.dump(
      response,
      indent=2,
      default_flow_style=None,
    )
    headers = {
      'Content-Type': media_type,
    }
    response = Response(
      content=content,
      media_type=media_type,
      headers=headers,
    )
  return response


async def get_response_handler(
  response: Any,
  request: Request,
) -> Any:
  _ = request
  return response


RESPONSE_HANDLER = {
  'GET': get_response_handler,
  'POST': post_response_handler,
}


@app.middleware("http")
async def add_response_time_to_header(
  request: Request,
  call_next: Callable,
) -> Any:
  start_time = time.time()
  response = await call_next(request)
  process_time = (time.time() - start_time) * 1000
  response.headers["Response-Time-MS"] = str(process_time)
  return response


@app.api_route(
  path='/{function_path}/',
  methods=['GET', 'POST'],
)
@app.api_route(
  path='/{function_path}',
  methods=['GET', 'POST'],
  include_in_schema=False,
)
async def process_request(request: Request,) -> Any:
  '''Single route to process all requests to the API'''
  setattr(request, 'data', models.Data())
  request = await format_path_params(request=request)

  # Route is used to determine which function to use
  function_path = request.data.path_params.function_path
  function_path = function_path.lower()
  function_data = f'''
    function:
      directory: {function_path}
  '''

  # Format request data based on content type and request method
  request = await format_request_headers(request=request)
  request_handler = REQUEST_HANDLER[request.method]
  request = await request_handler(request=request)

  # Get function and process request data
  function = await load_function_from_path.main(
    data=function_data)
  response = await function(request=request)

  response_handler = RESPONSE_HANDLER[request.method]
  response = await response_handler(
    response=response,
    request=request,
  )
  return response


async def start_server(env: 'Env') -> None:
  module_name = await get_this_module_name()
  uvicorn.run(
    f'{module_name}:app',
    host=env.API_HOST,
    port=int(env.API_PORT),
    reload=env.API_RELOAD,
    # workers=int(env.API_WORKERS),
  )


async def get_this_module_name(
  module_path: str = THIS_MODULE_PATH,
) -> str:
  path = pathlib.Path(module_path)
  file_name = path.stem
  return file_name


async def main() -> None:
  await start_server(env=ENV)


if __name__ == '__main__':
  import asyncio


  asyncio.run(main())

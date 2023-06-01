#! /usr/bin/python3

from os import path
import json
import dataclasses as dc
from fastapi import Request
from fastapi.templating import Jinja2Templates

from shared.load_function_from_path import app as load_function_from_path
from shared.get_environment import app as get_environment
from shared.format_main_arguments import app as format_main_arguments


MODULE_PATH = __file__
ENV = get_environment.main(module_path=MODULE_PATH)

# Upload limits
SERVER_UPLOAD_LIMIT_KB = 1024
MAX_HEADERS_SIZE_KB = 16


@dc.dataclass
class Query_Params:
  compression_level: int = 7
  server_upload_limit_kb: int = SERVER_UPLOAD_LIMIT_KB
  chunk_size_kb: int | None = None
  max_headers_size_kb: int = MAX_HEADERS_SIZE_KB
  coefficient: float = .95
  location: str = 'file_system'
  read_as: str = 'text'


@dc.dataclass
class Body:
  json: bytes | str | None = None
  binary: bytes | str | None = None


@dc.dataclass
class Method:
  value: str | None = None


@dc.dataclass
class Path_Params:
  function_path: str | None = None


@dc.dataclass
class Form:
  json: bytes | str | None = None
  binary: bytes | str | None = None


@dc.dataclass
class Data:
  query_params: Query_Params | None = None
  body: Body | None = None
  method: Method | None = None
  path_params: Path_Params | None = None
  form: Form | None = None


async def get_chunk_size_kb(
  query_params: Query_Params,
) -> Query_Params:
  chunk_size_kb = float(query_params.server_upload_limit_kb)
  chunk_size_kb -= float(query_params.max_headers_size_kb)
  chunk_size_kb = chunk_size_kb * query_params.coefficient
  return chunk_size_kb


async def get_handler(data: Data) -> Jinja2Templates:
  function_path = data.path_params.function_path
  function_path = function_path.split('.')

  chunk_size_kb = await get_chunk_size_kb(
    query_params=data.query_params)
  data.query_params.chunk_size_kb = chunk_size_kb

  directory = path.join(
    ENV.WORKDIR,
    *function_path,
    'static',
  )
  template = Jinja2Templates(
    directory=directory,
    auto_reload=ENV.API_RELOAD,
  )
  data = json.dumps(dc.asdict(data))
  html = template.TemplateResponse(
    'index.html', 
    context={
      'request': {},
      'data': data,
    },
  )
  return html


async def post_handler(data: Data) -> dict | Jinja2Templates:
  import_module_path = path.join(
    ENV.WORKDIR,
    *data.path_params.function_path.split('.'),
    'app.py',
  )
  function = {'directory': 'post'}
  function = await load_function_from_path.main(
    function=function,
    import_module_path=import_module_path,
  )
  response = await function(
    json=data.form.json,
    binary=data.form.binary,
  )
  return response


REQUEST_HANDLER = {
  'GET': get_handler,
  'POST': post_handler,
}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  # Query parameters
  compression_level: int | None = None,
  server_upload_limit_kb: int | None = None,
  chunk_size_kb: int | None = None,
  max_headers_size_kb: int | None = None,
  coefficient: float | None = None,
  location: str | None = None,
  read_as: str | None = None,
  # Form
  json: bytes | str | None = None,
  binary: bytes | str | None = None,
  # Method
  value: str | None = None,
  # Path parameters
  function_path: str | None = None,
) -> Jinja2Templates | dict:
  data_classes = {
    'body': Body,
    'query_params': Query_Params,
    'method': Method,
    'path_params': Path_Params,
    'form': Form,
  }
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes=data_classes,
    main_data_class=Data,
  )
  request = None
  request_handler = REQUEST_HANDLER[data.method.value]
  response = await request_handler(data=data)
  return response

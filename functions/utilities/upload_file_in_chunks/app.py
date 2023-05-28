#!/usr/bin/env python3

from os import path
import json
from dataclasses import (
  asdict,
  fields,
  dataclass,
  field,
)
from shelve import DbfilenameShelf
from fastapi.templating import Jinja2Templates

from api import models
from shared.load_function_from_path import app as load_function_from_path
from shared.get_environment import app as get_environment
from shared.get_persistant_storage import app as get_persistant_storage


MODULE_PATH = __file__
ENV = get_environment.main({'module_path': MODULE_PATH})
PERSITANT_STORAGE = None

# Upload limits
SERVER_UPLOAD_LIMIT_KB = 1024
MAX_HEADERS_SIZE_KB = 16


@dataclass
class QueryParams:
  compression_level: int = 7
  server_upload_limit_kb: int = SERVER_UPLOAD_LIMIT_KB
  chunk_size_kb: int | None = None
  max_headers_size_kb: int = MAX_HEADERS_SIZE_KB
  coefficient: float = .95
  location: str = 'file_system'
  read_as: str = 'text'


@dataclass
class Data(models.Data):
  query_params: QueryParams = field(default_factory=lambda:
    QueryParams())


@dataclass
class Request:
  data: Data = field(default_factory=lambda: Data())


async def process_query_params(
  request_query_params: QueryParams,
) -> QueryParams:
  query_params = QueryParams()
  for _field in fields(query_params):
    if not hasattr(request_query_params, _field.name):
      continue
    value = getattr(request_query_params, _field.name)
    setattr(query_params, _field.name, value)
  return query_params


async def get_chunk_size_kb(
  query_params: QueryParams,
) -> QueryParams:
  chunk_size_kb = float(query_params.server_upload_limit_kb)
  chunk_size_kb -= float(query_params.max_headers_size_kb)
  chunk_size_kb = chunk_size_kb * query_params.coefficient
  return chunk_size_kb


async def get_handler(
  request: Request,
  env: models.Env,
) -> Jinja2Templates:
  function_path = request.data.path_params.function_path
  function_path = function_path.split('.')
  
  chunk_size_kb = await get_chunk_size_kb(
    query_params=request.data.query_params)
  request.data.query_params.chunk_size_kb = chunk_size_kb
  
  directory = path.join(
    env.WORKDIR,
    *function_path,
    'static',
  )
  template = Jinja2Templates(
    directory=directory,
    auto_reload=env.API_RELOAD,
  )
  data = json.dumps(asdict(request.data))
  html = template.TemplateResponse(
    'index.html', 
    context={
      'request': request,
      'data': data,
    },
  )
  return html


async def set_persistant_storage() -> DbfilenameShelf:
  global PERSITANT_STORAGE
  if PERSITANT_STORAGE is None:
    PERSITANT_STORAGE = await get_persistant_storage.main()
  persistant_storage = PERSITANT_STORAGE
  return persistant_storage
  

async def post_handler(
  request: Request,
  env: models.Env,
) -> models.Response:
  import_module_path = path.join(
    env.WORKDIR,
    *request.data.path_params.function_path.split('.'),
    'app.py',
  )
  function_data = f'''
    function:
      directory: post
    import_module_path: {import_module_path}
  '''
  
  function = await load_function_from_path.main(
    data=function_data)
  persistant_storage = await set_persistant_storage()
  persistant_storage = persistant_storage.storage
  response = await function(
    request=request,
    persistant_storage=persistant_storage
  )
  return response


REQUEST_HANDLER = {
  'GET': get_handler,
  'POST': post_handler,
}


async def main(
  request: Request,
  env: models.Env = ENV,
  *args,
  **kwargs,
) -> Jinja2Templates | models.Response:
  request.data.query_params = await process_query_params(
    request_query_params=request.data.query_params)
  request_handler = REQUEST_HANDLER[request.method]
  response = await request_handler(
    request=request, env=env)
  return response


# async def format_multipart_content_json(
#   content: Any,
# ) -> models.DataClass:
#   content = content.decode('utf-8')
#   content = json.loads(content)
#   store = []
#   for key, value in content.items():
#     store.append([
#       key,
#       str,
#       field(default_factory=lambda: value),
#     ])
#   content_dataclass = make_dataclass('JSON', store)
#   return content_dataclass


# async def format_multipart_content_binary(
#   content: Any
# ) -> models.DataClass:
#   dataclass_fields = [[
#     'content',
#     ByteString,
#     field(default_factory=lambda: content),
#   ]]
#   content_dataclass = make_dataclass('Binary', dataclass_fields)
#   return content_dataclass


# MULTIPART_CONTENT_MAPPER = {
#   'json': format_multipart_content_json,
#   'binary': format_multipart_content_binary,
# }


# async def format_multipart_content(
#   content: Any,
#   part_name: str,
# ) -> dict:
#   function = MULTIPART_CONTENT_MAPPER[part_name]
#   result = await function(content=content)
#   return result

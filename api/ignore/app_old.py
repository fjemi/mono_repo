

from enum import Enum
from dataclasses import dataclass, field
from typing import (
  Callable, 
  Any, 
  List, 
  Dict, 
  Annotated,
  Optional,
)
from os import path
from importlib.machinery import SourceFileLoader
import sys
import yaml
import time
from ruamel.yaml import YAML
from fastapi import (
  FastAPI, 
  Body, 
  Request, 
  Header, 
  Response, 
  staticfiles, 
  templating,
  responses,
  File, 
  UploadFile,
)
import uvicorn
from requests_toolbelt.multipart import decoder
import os
import numpy as np
import io
import gzip
import sys

from shared.get_environment import app as get_environment


SERVER_UPLOAD_LIMIT_KB = 1024


ENV = get_environment.main(data=f'module_path: {__file__}')
PARENT_DIR = path.dirname(__file__)

TAGS_METADATA = '''
  - name: Routes
  - name: Any
    description: Route that support YAML or JSON for the request
      body, with request body type specified as a route parameter.
  - name: YAML
    description: Route that uses YAML for the request body
    externalDocs:
      description: YAML
      url: https://yaml.org/
  - name: JSON
    description: Route that uses JSON for the request body
    externalDocs:
      description: JSON
      url: https://www.json.org
  - name: Templates
    description: Services HTML templates and static files
'''
TAGS_METADATA = yaml.safe_load(TAGS_METADATA)
app = FastAPI(openapi_tags=TAGS_METADATA)

# Jinja2 Templates
templates_directory = path.join(PARENT_DIR, 'api', 'templates')
templates = templating.Jinja2Templates(directory=templates_directory)

# Serve static files
static_files_directory = path.join(PARENT_DIR, 'api', 'static')
app.mount(
  '/static',
  staticfiles.StaticFiles(directory=static_files_directory),
  name='static',
)

class Store:
  pass


class RequestBodyType(str, Enum):
  json = 'json'
  yaml = 'yaml'


async def load_function_from_path(
  function: str,
  module: str = 'app.py'
) -> Callable:
  module_path = path.join(
    PARENT_DIR, 
    'functions', 
    function, 
    module,
  )
  module = SourceFileLoader(
    function,
    module_path,
  ).load_module()
  function = getattr(module, 'main')
  return function


async def get_response_with_json_request(
  request: Request,
) -> Any:
  body = await request.json()
  function = await load_function_from_path(
    function=body['function'])
  if 'data' not in body.keys():
    body['data'] = None
  response = await function(data=body['data'])
  return response


async def get_response_with_yaml_request(
  request: Request,
) -> Any:
  body = await request.body()
  # body = yaml.safe_load(body)
  ruamel_yaml = YAML()
  body = ruamel_yaml.load(body)
  function = await load_function_from_path(
    function=body['function'])
  if 'data' not in body.keys():
    body['data'] = None
  response = await function(data=body['data'])
  return response


GET_RESPONSE = {
  'json': get_response_with_json_request,
  'yaml': get_response_with_yaml_request,
  # 'template': get_response_for_template_request,
}


async def get_response(
  request: Request, 
  content_type: str,
) -> Store:
  start_time = time.time()
  function = GET_RESPONSE[content_type]
  response = await function(request=request)
  run_time = time.time() - start_time
  run_time = round(run_time * 1000, 2)
  return response



ANY_POST_EXAMPLES = '''
  ping_json:
    summary: JSON - Ping
    description: Returns the result from pinging the API
    value: 
      function: ping
      data: null
  hello_world_w_data_json:
    summary: JSON - Hello World w/ Data
    description: A Hello World example
    value: 
      function: hello_world
      data: 
        name: Earth
  hello_world_wo_data_json:
    summary: JSON - Hello World w/o Data
    description: A Hello World example
    value: 
      function: hello_world
      data: null
  ping_yaml:
    summary: YAML - Ping
    description:
    value: |
      function: ping
      data: null
  hello_world_w_data_yaml:
    summary: YAML - Hello World w/ Data
    description:
    value: |
      function: hello_world
      data:
        name: Earth
  hello_world_wo_data_yaml:
    summary: YAML - Hello World w/o Data
    description:
    value: |
      function: hello_world
      data: null
'''
ANY_POST_EXAMPLES = yaml.safe_load(ANY_POST_EXAMPLES)


@app.post(
  '/any',
  tags=['Any'],
)
async def root_any(
  request: Request,
) -> Any:
  response = await get_response(
    request=request,
    content_type='yaml',
  )
  return response
  

# app.get('/{function}', tags=['Routes'])
# app.post('/{function}', tags=['Routes'])
@app.api_route(
  '/{function}', 
  methods=['get', 'post'],
  tags=['Routes'],
)
async def functional_route(
  request: Request,
  function: str,
) -> Any:
  function = await load_function_from_path(
    function=function,
  )
  response = await function(request=request)
  return response


@app.post('/form_data')
async def form_data(request: Request) -> Any:
  body = await request.body()

  headers = {}
  values = ['file_name', 'chunks_n', 'chunk_i']
  for value in values:
    headers[value] = request.headers.get(value)
  print(headers)
  
  setattr(request, 'content', body)
  multipart_data = decoder.MultipartDecoder.from_response(request)

  content = multipart_data.parts[0].content
  content = np.frombuffer(content, dtype=np.uint8)
  content = io.BytesIO(content).getvalue()
  
  import zlib
  content = zlib.decompress(content, zlib.MAX_WBITS|32)
  # print(content[:20])
  # content = io.StringIO(content)
  
  # content = gzip.GzipFile(fileobj=content)
  # content = content.read()
  # print(content[:20])
    
  print('decompressed', content[:40])
  print(type(content).__name__)
  
  # with open(
  #   f'{os.environ["DATA_PATH"]}/upload_file_in_chunks/Berserk - Ch.372 - 12_test_unzip.jpg',
  #   mode='wb',
    #encoding='utf-8',
  # ) as file:
    # import base64
    # file.write(base64.decodebytes(content))
    # file.write(content)
  

  with open(
    f'{os.environ["DATA_PATH"]}/upload_file_in_chunks/Berserk - Ch.372 - 12_test.jpg',
    mode='rb',
    #encoding='utf-8',
  ) as file:
    string = file.read()
    # string = string.decode('utf-8')
    print(string[:20])
  
  return None
  


JSON_POST_EXAMPLES = '''
  ping:
    summary: Ping
    description: Returns the result from pinging the API
    value: 
      function: ping
      data: null
  hello_world:
    summary: Hello World w/ Data
    description: A Hello World example
    value: 
      function: hello_world
      data: 
        name: Earth
  hello_world:
    summary: Hello World w/o Data
    description: A Hello World example
    value: 
      function: hello_world
      data: null
'''
JSON_POST_EXAMPLES = yaml.safe_load(JSON_POST_EXAMPLES)


@app.post('/json', tags=['JSON'])
async def root_json(
  request: Request,
) -> Any:
  response = await get_response(
    request=request,
    content_type='json',
  )
  return response

YAML_POST_EXAMPLES = '''
  Ping:
    summary:
    description:
    value: |
      function: ping
      data: null
  Hello World w/ Data:
    summary:
    description:
    value: |
      function: hello_world
      data:
        name: Earth
  Hello World w/o Data:
    summary:
    description:
    value: |
      function: hello_world
      data: null
'''  
YAML_POST_EXAMPLES = yaml.safe_load(YAML_POST_EXAMPLES)


@app.post('/yaml', tags=['YAML'])
async def root_yaml(
  request: Request,
) -> Any:
  response = await get_response(
    request=request,
    content_type='yaml',
  )
  return response


@app.get(
  '/template/{template}', 
  response_class=responses.HTMLResponse,
)
@app.get(
  '/template/{template}/{data}', 
  response_class=responses.HTMLResponse,
)
async def get_template(
  request: Request, 
  template: str,
  data: str | None = {},
):
  # body = await request.body()
  # body = yaml.safe_load(body)
  function = await load_function_from_path(
    function=template)
  # if 'data' not in body.keys():
  #   body['data'] = None
  response = await function(data=None)
  return response
  


@app.get(
  '/hello/',
  response_class=responses.HTMLResponse,
  tags=['Templates'],
)
@app.get(
  '/hello/{name}',
  response_class=responses.HTMLResponse,
  tags=['Templates'],
  include_in_schema=False,
)
async def hello_world_template(
  request: Request,
  name: str | None = 'World'
) -> str:
  test = dir(request)
  test2 = [
    request.query_params, 
    request._query_params, 
    request.path_params,
    request.headers,
    request.url,
  ]
  print(test, 'test2', test2)
  response = templates.TemplateResponse(
    'hello.html', 
    {'request': request},
  )
  return response


@app.get(
  '/upload/',
  response_class=responses.HTMLResponse,
  tags=['Upload', 'Templates'],
)
@app.get(
  '/upload/{compression_level}/{coefficient}',
  response_class=responses.HTMLResponse,
  tags=['Upload', 'Templates'],
  include_in_schema=False,
)
async def upload_template(
  request: Request,
  compression_level: str | None = 7,
  coefficient: str | None = .85,
) -> str:
  # Determine the chunk or slice size
  slice_size_kb = int(coefficient * SERVER_UPLOAD_LIMIT_KB)
  response = templates.TemplateResponse(
    'upload.html', 
    {
      'request': request, 
      'slice_size_kb': slice_size_kb,
      'compression_level': compression_level,
    },
  )
  return response


async def save_files_to_disk(
  files: 'UploadFile',
  upload_path: str,
) -> List[str]:
  store = []
  for file in files:
    store.append(file.filename)
    write_file_path = path.join(upload_path, file.filename)
    with open(write_file_path, 'wb+') as write_file:
      content = await file.read()
      write_file.write(content)
  return store


# async def unchunk_files(file_names: List[str]) -> List[str]:
#   store = []
#   for file_name in file_names:
#     if file_name.find('chunk@') == -1:
#       store.append(file_name)
#       continue
    
#   return store
  


@app.post('/upload/', tags=['Upload'])
async def upload_files(
  files: Annotated[
    list[UploadFile],
    File(description='Multiple files as UploadFile')
  ],
) -> dict | str: 
  upload_path = path.join(
    ENV.DATA_PATH,
    'fastapi',
  )
  file_names = await save_files_to_disk(
    files=files,
    upload_path=upload_path,
  )
  unchunked_file_names = await unchunk_files(
    file_names=file_names)
  return {'file_names': unchunked_file_names}


def run_server(env: 'Env') -> None:
  uvicorn.run(
    'app:app', 
    host=env.API_HOST, 
    port=int(env.API_PORT), 
    reload=env.API_RELOAD,
  )


if __name__ == '__main__':
  run_server(env=ENV)

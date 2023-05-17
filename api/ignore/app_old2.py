

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
  Path,
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
import io
import sys
import shelve

from shared.get_environment import app as get_environment
from shared.load_function_from_path import app as load_function_from_path2


ENV = get_environment.main(f'module_path: {__file__}')
PARENT_DIR = path.dirname(__file__)
THIS_FILE_PATH = __file__
# For persistant storage across API calls
PERSISTANT_STORAGE = shelve.open('shelve')




@dataclass
class PostData:
  function: str = None
  data: dict | None = None


METADATA = '''
  tags:
  - name: Routes
    description: Routes description
  - name: Functions
    description: Functions description
  - name: Pages
    description: Pages description
  openapi_extra:
    post:
      requestBody:
        content:
          application/json:
            schema: 
              RequestBody:
                type: object
                properties:
                  function:
                    type: string
                  data:
                    type: string
            example: 
              function: hello_world
              data:
                name: Earth
          text/plain:
            schema: 
              type: string
            example: |
              function: hello_world
              data:
                name: Earth
    get: 
      parameters:
      # - in: path
      #   name: function
      #   schema:
      #     type: string
      #   example: hello_world
      #   description: 
      - in: query
        name: params
        schema:
          type: list
        example: name
        description: A list of comma seperated query parameter names
      - in: query
        name: values
        schema:
          type: list
        example: Earth
        description: A list of comma seperated query parameter values
'''
METADATA = yaml.safe_load(METADATA)
app = FastAPI(openapi_tags=METADATA['tags'])


async def load_function_from_path(
  function: str,
  module: str = 'app.py',
  root_dir: str = PARENT_DIR,
) -> Callable:
  # function = function.split('.')

  module_path = path.join(
    root_dir, 
    'functions', 
    function, 
    module,
  )
  print('module_path', module_path)
  module = SourceFileLoader(
    function[-1],
    module_path,
  ).load_module()
  function = getattr(module, 'main')
  return function


async def format_query_params(request: Request) -> dict:
  params = request.query_params._dict
  if params == {}:
    return request

  for key, value in params.items():
    value = value.split(',')
    params[key] = value

  store = {}
  n = len(params['params'])
  for i in range(n):
    key = params['params'][i]
    value = params['values'][i]
    store[key] = value

  del request.query_params._dict
  setattr(request.query_params, '_dict', store)
  return request


@app.get('/{function}', include_in_schema=False)
@app.get(
  '/{function}/',
  tags=['Routes'],
  openapi_extra=METADATA['openapi_extra']['get'],
)
async def get_handler(
  request: Request,
  function: str = Path(
    ...,
    description='Function to call to',
    example='hello_world',
  ),
) -> 'Any':
  request = await format_query_params(request=request)
  
  # function_directory = function
  # function_data = f'''
  #   function:
  #     name: main
  #     module: app.py
  #     directory: {function_directory}
  #   import_module_path: {THIS_FILE_PATH}
  # '''
  # print(function_data)
  # function2 = await load_function_from_path2.main(data=function_data)
  # print(function2)

  function = await load_function_from_path(function=function)
  response = await function(
    request=request,
    persistant_storage=PERSISTANT_STORAGE,
  )
  return response


async def handle_application_json(request: Request) -> dict:
  body = await request.json()
  body = PostData(**body)
  setattr(request, 'data', body)
  request.json = None
  return request


async def handle_text_plain(request: Request) -> Request:
  body = await request.body()
  body = yaml.safe_load(body)
  body = PostData(**body)
  setattr(request, 'data', body)
  request.body = None
  return request


async def handle_multipart_form_data(request: Request) -> Request:
  form = await request.body()
  body = {
    'function': request.path_params['function'],
    'data': {
      'form': form,
    },
  }
  body = PostData(**body)
  setattr(request, 'data', body)
  request.body = None
  return request


REQUEST_HANDLER = {
  'application/json': handle_application_json,
  'text/plain': handle_text_plain,
  'multipart/form-data': handle_multipart_form_data,
}  


@app.post('/{function}', include_in_schema=False)
@app.post('/{function}/')
@app.post(
  '/',
  tags=['Routes'],
  openapi_extra=METADATA['openapi_extra']['post'],
)
async def post_handler(
  request: Request,
  # persistant_storage: 'shelve | None' = None,
  function: str | None = None,
) -> 'Any':
  content_type = request.headers.get('Content-Type')

  for key in REQUEST_HANDLER.keys():
    if content_type.find(key) == -1:
      continue
    content_type = key

  request_handler = REQUEST_HANDLER[content_type]
  request = await request_handler(request=request)
  function = request.data.function
  function = await load_function_from_path(function=function)
  response = await function(
    request=request,
    persistant_storage=PERSISTANT_STORAGE,
  )
  return response


async def set_persistant_storage_location(env: 'Env') -> bool:
  global PERSISTANT_STORAGE
  location = path.join(env.DATA_PATH, 'persistant_storage')
  PERSISTANT_STORAGE = shelve.open(location)
  return True


async def run_server(env: 'Env') -> None:
  uvicorn.run(
    'app:app', 
    host=env.API_HOST, 
    port=int(env.API_PORT), 
    reload=env.API_RELOAD,
  )
  
  
if __name__ == '__main__':
  import asyncio
  
  
  # asyncio.run(set_persistant_storage_location(env=ENV))
  asyncio.run(run_server(env=ENV))

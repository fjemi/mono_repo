#!/usr/bin/env python3

# External
import uvicorn
from fastapi import FastAPI, Request, Header
from pydantic import BaseModel
from typing import Any
# Standard
from dataclasses import dataclass, asdict
import os
import sys
import json
# Internal
from shared.load_function_from_path.load_function_from_path import load_function_from_path


@dataclass
class Data:
  name: str = os.getenv('APP_NAME') or 'app'
  version = os.getenv('APP_VERSION') or 'v1'
  root_dir = os.getenv('ROOT_DIR') or '..'


class PostData(BaseModel):
  function: str = 'hello_world'
  data: dict | None = None
  header: dict | None = None
  

class GetData(BaseModel):
  pass


data = Data()
app = FastAPI(**asdict(data))


# @app.get('/')
# async def root(request: Request) -> dict:
#   '''
#   Example Request
#     http://localhost:8000/?data={"data":{"hello":"mars"},"function":"hello_world"}
#   '''
#   # Query parameterss to dictionary
#   params = request.query_params._dict
#   # Get function and execute with data
#   data = json.loads(params['data'].replace('"', '"'))
#   function_data = {'function_name': data['function']}
#   function = load_function_from_path(data=function_data)
#   return function(data['data'])


@app.get('/')
async def root(data) -> dict:
  '''
  ## Get Request
  ### Summary
  Handle post requests.
  ### Parameters
  - **function**: A function to call
  - **data**: data to pass as arguements to the function
  ### Returns
  The results of executing the function
  ###Example Request
  http://localhost:8000/?data={"data":{"hello":"mars"},"function":"hello_world"}
  '''
  print(data)
  data = json.loads(data)
  function = load_function_from_path(data={'function_name': data['function']})
  result = function(data['data'])
  return result



@app.post('/')
async def root(request: PostData) -> dict:
  '''
  ## Post Request
  ### Summary
  Handle post requests.
  ### Parameters
  - **function**: A function to call
  - **data**: data to pass as arguements to the function
  ### Returns
  The results of executing the function
  ### Example Request
    `curl -X 'POST' \
      'http://localhost:8000/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "function": "hello_world",
      "data": {"hello": "mars"},
      "header": {}
    }'`
  '''
  # TODO dynamically get request attributes
  # Await to get contents of request
  # contents =curl -X 'POST' 'http://0.0.0.0:8000/' -H 'accept: application/json' -d '{function:hello_world}' ['headers', 'body', ]
  # store = {}
  # for content in contents:
  #   try:
  #     store[content] = await getattr(request, content)()
  #   except:
  #     pass
  # print(store)

  # TODO 
  # Load YML for function. YAML should contain required request attributes (headers, body, form, etc)
  # Load function
  # Pass attributes to function

  # Load and execute function
  data = {'function_name': request.function}
  function = load_function_from_path(data=data)
  result = function(request.data)
  return result


if __name__ == '__main__':
  uvicorn.run(
    'app:app',
    host="0.0.0.0",
    port=8000,
    reload=True, 
    workers=2, )


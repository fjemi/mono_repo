#!/usr/bin/env python3

from dataclasses import dataclass
from os.path import split, realpath
from importlib.machinery import SourceFileLoader
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query, status, HTTPException

from shared.get_env_vars import get_env_vars

# set app root directory
API_DIR = split(realpath(__file__))[0]
ENV = get_env_vars()

class Payload(BaseModel):
  '''
  # Request Payload Model
  - **route**: route in `/routes` 
  - **data**: data passed to function loaded 
  '''
  route: str = 'ping'
  data: Any = {}
  

app = FastAPI(
  title=ENV.name,
  version=ENV.tag
)


@app.get('/')
async def root() -> dict:
  '''
  # Ping the API
  ---
  '''
  # TODO: use secure protocol for docs url
  swagger_docs_url = f'http://{ENV.host}:{ENV.port}/docs'
  redoc_docs_url = None
  return {
    'name': ENV.name, 
    'swagger_docs': swagger_docs_url,
    'redoc_docs': redoc_docs_url}

@app.get('/api/{route}/')
async def api(route: str, q: Optional[List[str]] = Query(None)) -> dict:
  '''
  # API Get Requests
  ---
  Parameters
  - **route**: function to call
  - **q**: optional list of query parameters
  '''
  # TODO implement functionality similar to post request
  query_items = {"q": q}
  return route, query_items

@app.post('/api')
async def api(payload: Payload) -> dict:
  '''
  # API Post Requests
  ___
  Payload
  - **route**: function to call
  - **data**: optional data to pass
  '''
  # check if the payload contains a route
  if 'route' not in payload.dict().keys():
    return HTTPException

  try:
    # load routes defined in `/routes` folder
    route = SourceFileLoader(payload.route,
      f'{API_DIR}/routes/{payload.route}.py'
    ).load_module()
    
    # load function from route
    func = getattr(route, payload.route)
    return func(payload.data)
  except Exception as error:
    return {'error': repr(error)}


def run_server():
  ''''''
  import uvicorn
  uvicorn.run('app:app', host=ENV.host, port=int(ENV.port), reload=ENV.debug)


if __name__ == "__main__":
  run_server()

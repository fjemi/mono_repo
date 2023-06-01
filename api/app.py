#!/usr/bin/env python3

from typing import Any, Callable
import pathlib
import time
from fastapi import FastAPI, Request
import uvicorn


from shared.get_environment import app as get_environment
from shared.load_function_from_path import app as load_function_from_path
from api.openapi import app as openapi


THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)


app = FastAPI()

# Set the OpenAPI schema for the app
openapi_schema = openapi.main(app_module_path=THIS_MODULE_PATH)
app.openapi_schema = openapi_schema.schema
ROUTES = openapi_schema.routes


@app.middleware("http")
async def add_response_time_to_header(
  request: Request,
  call_next: Callable,
) -> Any:
  start_time = time.time()
  response = await call_next(request)
  process_time = (time.time() - start_time) * 1000
  response.headers["Response-Time-MS"] = f'{process_time:.3f}'
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

  # Route is used to determine which function to use
  function_path = request.path_params['function_path']
  function_path = function_path.lower()
  # Get function and process request data
  function = await load_function_from_path.main(
    function={'directory': function_path}
  )
  response = await function(request=request)
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

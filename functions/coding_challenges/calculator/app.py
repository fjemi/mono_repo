#!usr/bin/env python3

from typing import List, Any, Dict, Callable
import dataclasses as dc
import os
from runpy import run_path
import yaml
from fastapi.templating import Jinja2Templates
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments
from shared.get_environment import app as get_environment

THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)

FUNCTIONS = None


@dc.dataclass
class Body:
  operations: List[dict] | List[str] | dict | str | None = None


@dc.dataclass
class Operation:
  name: str | None = None
  inputs: List[int | float | List] | None = None
  result: Any = 0
  chain: bool = False


@dc.dataclass
class Data:
  body: Body | None = None
  results: List[Operation] | None = None





async def get_functions(
  functions: Dict[str, Callable] = FUNCTIONS,
) -> Dict[str, Callable]:
  if functions:
    return functions
  path = os.path.join(
    os.path.dirname(THIS_MODULE_PATH),
    'get_operations',
    'app.py',
  )
  module = run_path(path)
  functions = await module['main'](app_module_path=THIS_MODULE_PATH)
  global FUNCTIONS
  FUNCTIONS = functions
  return functions


async def process_arguments_request_call(_locals: dict) -> Data:
  request = _locals['request'].data.body
  data = Data(body=Body())
  for field in dc.fields(data.body):
    if not hasattr(request, field.name):
      continue
    value = getattr(request, field.name)
    if value is None:
      continue
    setattr(data.body, field.name, value)
  return data


async def process_arguments_module_call(_locals: dict) -> Data:
  ignore_arguments = ['request', 'functions']
  data = Data(body=Body())
  for key, value in _locals.items():
    if key in ignore_arguments or value is None:
      continue
    setattr(data.body, key, value)
  return data


PROCESS_MAIN_ARGUMENTS = {
  'api': process_arguments_request_call,
  'module': process_arguments_module_call, 
}


async def process_main_arguments(_locals: dict) -> Data:
  _locals['call_method'] = 'api' if _locals['request'] else 'module'
  switcher = PROCESS_MAIN_ARGUMENTS[_locals['call_method']]
  data = await switcher(_locals=_locals)

  if isinstance(data.body.operations, str):
    data.body.operations = yaml.safe_load(data.body.operations)
  if not isinstance(data.body.operations, list):
    data.body.operations = [data.body.operations]
  return data


async def handle_get_request(
  request: Request,
  functions: Dict[str, Callable],
) -> Data:
  # _case = hasattr(request.data.query_params, 'name')
  # switch = GET_DATA_SWITCH[_case]
  # request.data.query_params = switch(
  #   query_params=request.data.query_params)

  directory = os.path.dirname(THIS_MODULE_PATH)
  directory = os.path.join(directory, 'static')
  template = Jinja2Templates(
    directory=directory,
    auto_reload=ENV.API_RELOAD,
  )

  # function_list = list(functions.keys())
  # data = json.dumps(dc.asdict(request.data))
  template = template.TemplateResponse(
    'index.html',
    context={
      'request': request,
      'data': functions,
    },
  )
  return template


async def process_request_body(
  request: Request,
) -> Data:
  body = Body()
  for field in dc.fields(body):
    if not hasattr(request.data.body, field.name):
      continue
    value = getattr(request.data.body, field.name)
    if value is None:
      continue
    setattr(body, field.name, value)
  data = Data(body=body)
  return data


async def process_operations(
  data: Data,
  functions: Dict[str, Callable],
) -> Data:
  store = [Operation()]
  for operation in data.body.operations:
    operation = Operation(**operation)
    if operation.chain:
      answer = store[-1].result
      operation.inputs.append(answer)

    if not operation.name:
      operation.result = list(functions.keys())

    if operation.name:
      function = functions[operation.name]
      operation.result = await function(
        inputs=operation.inputs,
        operation=operation.name,
      )
    store.append(operation)
  data.results = store[1:]
  return data


async def get_response(data: Data) -> dict | Jinja2Templates:
  data = data.results
  data = dict(data=data)
  return data


async def handle_post_request(
  request: Request,
  functions: Dict[str, Callable],
) -> Data:
  data = await process_request_body(request=request)
  data = await process_operations(
    data=data,
    functions=functions,
  )
  # data = await get_response(data=data)
  data = dict(data=data.results)
  return data


REQUEST_HANDLER = {
  'GET': handle_get_request,
  'POST': handle_post_request,
}


async def main(
  request: Request,
) -> dict | Jinja2Templates:
  functions = await get_functions()
  handler = REQUEST_HANDLER[request.method]
  data = await handler(
    request=request,
    functions=functions,
  )
  return data

#!/usr/bin/env python3

import dataclasses as dc
from os import path
import json
from fastapi import Request
from fastapi.templating import Jinja2Templates

from shared.get_environment import app as get_environment
from shared.format_main_arguments import (
  app as format_main_arguments)


THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)


@dc.dataclass
class Query_Params:
  name: str = 'World'


@dc.dataclass
class Body:
  name: str = 'World'


@dc.dataclass
class Method:
  value: str = 'GET'


@dc.dataclass
class Data:
  query_params: Query_Params | None = None
  body: Body | None = None
  method: Method | None = None


GET_SWITCHER = {
  False: lambda query_params: Query_Params(),
  True: lambda query_params: query_params,
}


async def get_handler(
  data: Data,
  request: Request,
) -> Jinja2Templates:
  cases = hasattr(data.query_params, 'name')
  switch = GET_SWITCHER[cases]
  data.query_params = switch(query_params=data.query_params)

  directory = path.dirname(THIS_MODULE_PATH)
  directory = path.join(directory, 'static')
  template = Jinja2Templates(
    directory=directory,
    auto_reload=ENV.API_RELOAD,
  )

  data = json.dumps(dc.asdict(data))
  template = template.TemplateResponse(
    'index.html', 
    context={
      'request': request,
      'data': data,
    },
  )
  return template


POST_SWITCHER = {
  True: lambda body: body.name,
  False: lambda body: 'World',
}


async def post_handler(
  data: Data,
  request: Request,
) -> dict:
  _ = request
  cases = hasattr(data.body, 'name')
  switcher = POST_SWITCHER[cases]
  name = switcher(body=data.body)
  text = 'Hello World!'.replace('World', name.title())
  data = {'data': text}
  return data


REQUEST_HANDLER = {
  'GET': get_handler,
  'POST': post_handler,
}


async def process_request(
  data: Data,
  request: Request,
) -> Data:
  _ = request
  handler = REQUEST_HANDLER[data.method.value]
  data = await handler(
    data=data,
    request=request,
  )
  return data


async def main(
  request: Request,
  *args,
  **kwargs,
) -> dict | Jinja2Templates:
  _ = args, kwargs
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={
      'body': Body,
      'query_params': Query_Params,
      'method': Method,
    },
    main_data_class=Data,
  )
  data = await process_request(
    data=data,
    request=request,
  )
  return data

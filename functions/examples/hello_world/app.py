#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict
from os import path
import json
from fastapi.templating import Jinja2Templates

from api import models as api_models
from shared.get_environment import app as get_environment


THIS_FILE_PATH = __file__
ENV = get_environment.main({'module_path': THIS_FILE_PATH})


@dataclass
class QueryParams:
  name: str = 'World'


@dataclass
class Body:
  data: str = 'Hello World!'


@dataclass
class Data:
  query_params: QueryParams = field(
    default_factory=lambda: QueryParams())
  body: Body = field(default_factory=lambda: Body())


@dataclass
class Request:
  data: Data | None = None
  method: str = 'GET'


POST_DATA_SWITCH = {
  1: lambda request: request.data.body,
  0: lambda request: Body(),
}


async def post_handler(request: api_models.Request) -> dict:
  _case = int(hasattr(request.data.body, 'name'))
  switch = POST_DATA_SWITCH[_case]
  data = switch(request=request)
  text = 'Hello World!'.replace('World', data.name)
  data = {'data': text}
  return data


GET_DATA_SWITCH = {
  0: lambda query_params: QueryParams(),
  1: lambda query_params: query_params,
}


async def get_handler(
  request: Request,
) -> Jinja2Templates:
  _case = hasattr(request.data.query_params, 'name')
  switch = GET_DATA_SWITCH[_case]
  request.data.query_params = switch(
    query_params=request.data.query_params)

  directory = path.dirname(THIS_FILE_PATH)
  directory = path.join(directory, 'static')
  template = Jinja2Templates(
    directory=directory,
    auto_reload=ENV.API_RELOAD,
  )

  data = json.dumps(asdict(request.data))
  template = template.TemplateResponse(
    'index.html', 
    context={
      'request': request,
      'data': data,
    },
  )
  return template


REQUEST_METHOD_SWITCH = {
  'POST': post_handler,
  'GET': get_handler,
}


async def main(
  request: Request,
  *args,
  **kwargs,
) -> dict | Jinja2Templates:
  _ = args, kwargs
  _case = request.method
  switch = REQUEST_METHOD_SWITCH[_case]
  response = await switch(request=request)
  return response


async def example() -> None:
  response = {
    'GET': await main(request=Request(method='GET')),
    'POST': await main(request=Request(method='POST')),
  }
  print(response)


if __name__ == '__main__':
  import asyncio


  asyncio.run(example())

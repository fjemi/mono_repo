#!/usr/bin/env python3

from dataclasses import dataclass, fields, field
from typing import Any, List, Dict, Callable
from copy import deepcopy
from datetime import datetime
import json
import boto3
import yaml
from fastapi import HTTPException

from api import models as api_models
from shared.get_environment import app as get_environment


THIS_MODULE_PATH = __file__
ENV = get_environment.main({'module_path': THIS_MODULE_PATH})

# Caches session and clients to reduce instantiations
SESSION = None
CLIENTS = {}


@dataclass
class Body(api_models.Body):
  client: str | None = None
  method: str | None = None
  parameters: Any | None = None
  response: Any | None = None
  parse_response: List[str] | None = None
  error: Any | None = None


@dataclass
class Data:
  body: Body | None = None
  session: boto3.Session | None = field(default_factory=lambda: SESSION)
  clients: Dict[str, boto3.client] = field(default_factory=lambda: CLIENTS)


async def process_call_from_api(
  request: api_models.Request,
  service: None = None,
) -> Data:
  _ = service
  body = Body()

  for _field in fields(body):
    if not hasattr(request.data.body, _field.name):
      continue
    value = getattr(request.data.body, _field.name)
    if not value:
      continue
    setattr(body, _field.name, value)

  data = Data(body=body)
  return data


async def process_call_from_module(
  service: str | dict,
  request: None = None,
) -> Data:
  _ = request
  if isinstance(service, str):
    service = yaml.safe_load(service)

  body = Body(**service)
  data = Data(body=body)
  return data


PROCESS_MAIN_ARGUMENTS = {
  'api_call': process_call_from_api,
  'module_call': process_call_from_module,
}


async def process_main_arguments(
  request: api_models.Request,
  service: str | dict,
) -> Data:
  cases = 'api_call' if request else 'module_call'
  switcher = PROCESS_MAIN_ARGUMENTS[cases]
  data = await switcher(
    request=request,
    service=service,
  )
  return data


async def get_session(data: Data) -> Data:
  if data.session:
    return data

  global SESSION
  SESSION = boto3.session.Session(
    aws_access_key_id=ENV.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=ENV.AWS_SECRET_ACCESS_KEY,
    region_name=ENV.AWS_REGION_NAME,
  )
  data.session = SESSION
  return data


async def get_client(
  session: boto3.Session,
  service_name: str,
  clients: Dict[str, boto3.client],
) -> Dict[str, boto3.client]:
  if service_name in clients:
    client = clients[service_name]
    return client

  services = session.get_available_services()
  if service_name not in services:
    raise HTTPException(
      status_code=400,
      detail=f'{service_name} does not exist'
    )

  # pylint: disable=global-variable-not-assigned
  global CLIENTS
  client = session.client(service_name=service_name)
  CLIENTS[service_name] = client
  return client


async def get_client_method(
  client: boto3.client,
  method: str,
) -> Callable:
  if not hasattr(client, method):
    service = type(client).__name__
    raise HTTPException(
      status_code=400,
      detail=f'{service} does not have the method {method}',
    )
  method = getattr(client, method)
  return method


GET_RESPONSE = {
  0: lambda method, parameters: method(),
  1: lambda method, parameters: method(parameters),
  2: lambda method, parameters: method(*parameters),
  3: lambda method, parameters: method(**parameters),
  4: lambda method, parameters: method,
}


async def get_client_method_response(
  method: Callable,
  parameters: Any | None,
) -> Any:
  params_type = type(parameters).__name__
  params_type = params_type.lower()

  conditions = {
    params_type == 'nonetype': 0,
    params_type not in ['nonetype', 'dict', 'list', 'tuple']: 1,
    params_type in ['list', 'tuple']: 2,
    params_type == 'dict': 3,
  }
  index = conditions[1]
  function = GET_RESPONSE[index]

  response = None
  try:
    response = function(
      parameters=parameters,
      method=method,
    )
  except Exception as e:
    detail = {
      'exception': type(e).__name__,
      'message': str(e).split('\n'),
    }
    # pylint: disable=raise-missing-from
    raise HTTPException(
      status_code=500,
      detail=detail,
    )
  return response


async def parse_response_list(
  key: str,
  response: List[Any],
) -> List[Any]:
  store = []
  for item in response:
    value = item[key]
    store.append(value)
  return store


async def parse_response_dict(key: str, response: dict) -> dict:
  response = response[key]
  return response


PARSE_RESPONSE = {
  'list': parse_response_list,
  'dict': parse_response_dict,
}


def convert_datetime_to_seconds(json_object: Any):
  if isinstance(json_object, datetime):
    return json_object.timestamp()


async def parse_response(body: Body) -> Body:
  response_type = type(body.response).__name__.lower()
  conditions = [
    body.parse_response in ['', None],
    body.response in [[], {}, None],
    response_type not in ['dict', 'list', 'nonetype'],
  ]
  if True in conditions:
    return body

  store = []

  for parsers in body.parse_response:
    keys = parsers.split('.')
    response = deepcopy(body.response)
    for key in keys:
      response_type = type(response).__name__
      switcher = PARSE_RESPONSE[response_type]
      response = await switcher(
        key=key,
        response=response,
      )
    response = {parsers: response}
    store.append(response)

  body.response = store
  return body


async def process_service_request(data: Data) -> Data:
  body = deepcopy(data.body)
  if isinstance(body, str):
    body = yaml.safe_load(body)

  client = await get_client(
    session=data.session,
    service_name=body.client,
    clients=data.clients,
  )
  method = await get_client_method(
    client=client,
    method=body.method,
  )
  body.response = await get_client_method_response(
    method=method,
    parameters=body.parameters,
  )
  # Convert datetime objects to seconds since epoch
  body.response = json.dumps(
    body.response,
    default=convert_datetime_to_seconds,
  )
  body.response = json.loads(body.response)
  body = await parse_response(body=body)
  return body


async def get_response(data: Data) -> api_models.Response:
  data = api_models.Response(data=data.response)
  return data


async def main(
  request: api_models.Request | None = None,
  service: str | None = None,
) -> api_models.Response | dict:
  data = await process_main_arguments(
    request=request,
    service=service,
  )
  data = await get_session(data=data)
  data = await process_service_request(data=data)
  data = await get_response(data=data)
  return data


async def example() -> None:
  service = '''
    client: s3
    method: list_buckets
    parameters: null
    parse_response:
    - Buckets.Name
    - Buckets.CreationDate
  '''
  result = await main(service=service)
  print(result)


if __name__ == '__main__':
  import asyncio


  asyncio.run(example())

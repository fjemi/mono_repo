#!/usr/bin/env python3

from dataclasses import dataclass, fields, field
from typing import Any, List, Dict, Callable
from copy import deepcopy
from datetime import datetime
import json
import boto3
import yaml


from api import models as api_models
from shared.get_environment import app as get_environment


THIS_MODULE_PATH = __file__
ENV = get_environment.main({'module_path': THIS_MODULE_PATH})

# Caches session and clients to reduce instantiations
SESSION = None
CLIENTS = {}


@dataclass
class Service:
  name: str | None = None
  parameters: Any | None = None
  parse_response: List[str] | None = None
  response: Any | None = None
  error: Any | None = None


@dataclass
class Body(api_models.Body):
  services: List[dict] | str | None = None


@dataclass
class Data:
  body: Body | None = None
  api_call: bool = False
  session: boto3.Session | None = field(default_factory=lambda: SESSION)
  clients: Dict[str, boto3.client] = field(default_factory=lambda: CLIENTS)
  services: List[Service] | None = None


async def process_request_argument(
  _locals: dict,
  data: Data = Data,
  body: Body = Body,
) -> Data:
  request = _locals['request']

  body = body()
  for _field in fields(body):
    if not hasattr(request.data.body, _field.name):
      continue
    value = getattr(request.data.body, _field.name)
    if not value:
      continue
    setattr(body, _field.name, value)

  data = data(body=body, api_call=True)
  return data


async def process_non_request_arguments(
  _locals: dict,
  data: Data = Data,
  body: Body = Body,
) -> Data:
  body = body()
  for _field in fields(body):
    if _field.name not in _locals:
      continue
    value = _locals[_field.name]
    if not value:
      continue
    setattr(body, _field.name, value)
  data = data(body=body)
  return data


PROCESS_MAIN_ARGUMENTS = {
  'request': process_request_argument,
  'non_request': process_non_request_arguments,
}


async def process_main_arguments(_locals: dict) -> Data:
  cases = 'request' if _locals['request'] else 'non_request'
  switcher = PROCESS_MAIN_ARGUMENTS[cases]
  data = await switcher(_locals=_locals)
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
    return clients

  global CLIENTS
  client = session.client(service_name=service_name)
  CLIENTS[service_name] = client
  return CLIENTS


async def get_request(client: boto3.client, request: str) -> Callable:
  request = getattr(client, request)
  return request


GET_RESPONSE = {
  0: lambda request, parameters: request(),
  1: lambda request, parameters: request(parameters),
  2: lambda request, parameters: request(*parameters),
  3: lambda request, parameters: request(**parameters),
  4: lambda request, parameters: request,
}


async def get_service_request_response(
  request: Callable,
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
  response = function(
    parameters=parameters,
    request=request,
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


async def parse_response(service: Service) -> Service:
  response_type = type(service.response).__name__.lower()
  conditions = [
    service.parse_response in ['', None],
    service.response in [[], {}, None],
    response_type not in ['dict', 'list', 'nonetype'],
  ]
  if True in conditions:
    return service

  store = []

  for parsers in service.parse_response:
    keys = parsers.split('.')
    response = deepcopy(service.response)
    for key in keys:
      response_type = type(response).__name__
      switcher = PARSE_RESPONSE[response_type]
      response = await switcher(
        key=key,
        response=response,
      )
    store.append(response)

  service.response = store
  return service


async def process_service_requests(data: Data) -> Data:
  services = deepcopy(data.body.services)
  if isinstance(services, str):
    services = yaml.safe_load(services)

  store = []
  for service in services:
    service = Service(**service)
    service_name, request = service.name.split('.')
    data.clients = await get_client(
      session=data.session,
      service_name=service_name,
      clients=data.clients,
    )
    client = data.clients[service_name]
    request = await get_request(
      client=client,
      request=request,
    )

    try:
      service.response = await get_service_request_response(
        request=request,
        parameters=service.parameters,
      )
    # pylint: disable=broad-exception-caught
    except Exception as exception:
      # pylint: disable=no-member
      service.error = exception.response['Error']

    # Convert datetime objects to seconds since epoch
    service.response = json.dumps(
      service.response,
      default=convert_datetime_to_seconds,
    )
    service.response = json.loads(service.response)
    service = await parse_response(service=service)
    store.append(service)

  data.services = store
  return data


async def get_response(data: Data) -> Data:
  store = []
  for service in data.services:

    # Error
    if service.error:
      response = f'''
        code: 500
        data:
          error: 
            {service.error}
          service: {service.name}
        status: error
      '''

    # OK
    if not service.error:
      n = len(service.response)
      response = {}
      for i in range(n):
        response[service.parse_response[i]] = service.response[i]
      response = f'''
        code: 200
        data:
          service: {service.name}
          response: {response}
        status: ok
      '''

    response = yaml.safe_load(response)
    store.append(response)
  return store


# pylint: disable=unused-argument
async def main(
  request: api_models.Request | None = None,
  services: str | List[str] | None = None,
) -> api_models.Response | dict:
  data = await process_main_arguments(_locals=locals())
  data = await get_session(data=data)
  data = await process_service_requests(data=data)
  data = await get_response(data=data)
  return data


async def example() -> None:
  services = '''
  - name: s3.list_buckets
    parameters: null
    parse_response:
    - Buckets.Name
    - Buckets.CreationDate
  '''
  result = await main(services=services)
  print(result)


if __name__ == '__main__':
  import asyncio


  asyncio.run(example())

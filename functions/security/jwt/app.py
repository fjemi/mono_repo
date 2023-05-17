#!/usr/bin/env python3

import jwt
from dataclasses import (
  dataclass,
  asdict,
  field,
  fields,
  make_dataclass,
  is_dataclass,
)
from typing import Dict, List, Any
import base64
import time

from api import models as api_models
from shared.get_environment import app as get_environment


THIS_MODULE_PATH = __file__
ENV = get_environment.main({'module_path': THIS_MODULE_PATH})


@dataclass
class Body:
  algorithm: str | List[str] = 'HS256'
  key: str | bytes | None = None
  operation: str | None = None
  payload: dict | None = None
  jwt: str | None = None


@dataclass
class Header:
  algorithm: str = 'HS256'
  type: str = 'JWT'


SEVEN_DAYS_IN_SECS = 604800


@dataclass
class Payload:
  # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1
  issuer: str | None = None
  subject: str | None = None
  audience: str | None = None
  expiration_time: int = field(
    default_factory=lambda: int(time.time()) + SEVEN_DAYS_IN_SECS)
  not_before: int = field(default_factory=lambda: int(time.time()))
  issued_at: int = field(default_factory=lambda: int(time.time()))
  jwt_id: str | None = None
  content: Any | None = None


@dataclass
class Data:
  body: Body | None = None
  api_request: bool = False
  env: api_models.Env = field(default_factory=lambda: ENV)
  result: str | dict | None = None


async def decode_base64_key(key: bytes) -> str:
  key = base64.b64decode(key)
  key = key.decode('utf-8')
  return key


async def return_key(key: str) -> str:
  return key


FORMAT_KEY = {
  'str': return_key,
  'bytes': decode_base64_key,
}


async def format_key(key: str | bytes) -> str:
  key_type = type(key).__name__
  switcher = FORMAT_KEY[key_type]
  key = await switcher(key=key)
  return key


async def encode_payload(data: Data) -> Data:
  if is_dataclass(data.body.payload):
    data.body.payload = asdict(data.body.payload)

  data.result = jwt.encode(
    payload=data.body.payload,
    key=data.body.key,
    algorithm=data.body.algorithm,
    # payload=data.payload,
    # header=data.header,
    # signature=data.signature,
  )
  return data


async def decode_payload(data: Data) -> Data:
  data.result = jwt.decode(
    jwt=data.body.jwt,
    key=data.body.key,
    algorithms=data.body.algorithm,
  )
  return data


PERFORM_OPERATION = {
  'encode': encode_payload,
  'decode': decode_payload,
}


NAME_MAPPER = {
  'RS256.encode': 'RS256_PRIVATE_KEY',
  'RS256.decode': 'RS256_PUBLIC_KEY',
  'HS256.encode': 'HS256_KEY',
  'HS256.decode': 'HS256_KEY',
}


async def preform_operation(data: Data) -> Data:
  _case = f'{data.body.algorithm}.{data.body.operation}'
  key_name = NAME_MAPPER[_case]
  key = getattr(data.env, key_name)
  data.body.key = key if not data.body.key else data.body.key
  data.body.key = await format_key(key=data.body.key)
  switcher = PERFORM_OPERATION[data.body.operation]
  data = await switcher(data=data)
  return data


async def process_request_args(_locals: dict) -> Data:
  request = _locals['request']

  body = Body()
  for _field in fields(request.data.body):
    value = getattr(request.data.body, _field.name)
    if value is None:
      continue
    setattr(body, _field.name, value)

  data = Data(body=body, api_request=True)
  return data


async def process_non_request_args(_locals: dict) -> Data:
  del _locals['request']

  body = Body()
  for key, value in _locals.items():
    if value is None:
      continue
    setattr(body, key, value)
  data = Data(body=body)
  return data


PROCESS_MAIN_ARGS = {
  'request': process_request_args,
  'non_request': process_non_request_args,
}


async def process_main_args(_locals: dict) -> Data:
  cases = 'request' if _locals['request'] else 'non_request'
  switcher = PROCESS_MAIN_ARGS[cases]
  data = await switcher(_locals=_locals)
  return data


async def get_jwt_as_response(data: Data) -> api_models.Response:
  data = {'jwt': data.result}
  data = api_models.Response(data=data)
  return data


async def get_payload_as_response(data: Data) -> api_models.Response:
  data = {'payload': data.result}
  data = api_models.Response(data=data)
  return data


async def get_jwt_as_string(data: Data) -> str:
  return data.result


async def get_payload_as_data_class(data: Data) -> Payload:
  cls_name = 'Payload'
  _fields = []

  for key, value in data.result.items():
    value_type = type(value).__name__
    field_value = field(default=value)
    if value_type not in ['int', 'str', 'float']:
      field_value = field(default_factory=lambda: value)
    _field = [
      key,
      value_type,
      field_value,
    ]
    _fields.append(_field)

  data_class = make_dataclass(cls_name=cls_name, fields=_fields)
  return data_class


GET_RESPONSE = {
  'request.encode': get_jwt_as_response,
  'request.decode': get_payload_as_response,
  '.encode': get_jwt_as_string,
  '.decode': get_payload_as_data_class,
}


async def get_response(data: Data) -> api_models.Response | str | Payload:
  cases = [
    int(data.api_request) * 'request',
    data.body.operation,
  ]
  cases = '.'.join(cases)
  switcher = GET_RESPONSE[cases]
  data = await switcher(data=data)
  return data


# This should be a decorator
# pylint: disable=unused-argument
async def main(
  request: api_models.Request | None = None,
  algorithm: str | None = None,
  key: str | bytes | None = None,
  payload: dict | Payload | None = None,
  header: dict | Header = None,
  jwt: Any | None = None,
  operation: Any | None = None,
) -> api_models.Response | dict | str:
  data = await process_main_args(_locals=locals())
  data = await preform_operation(data=data)
  data = await get_response(data=data)
  return data

#!/usr/bin/env python3

import dataclasses as dc
import time
from typing import Any, List
import base64
# import time
import json
import jwt
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments
from shared.get_environment import app as get_environment
from shared.format_main_arguments import app as format_main_arguments


THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)


@dc.dataclass
class Body:
  algorithm: str | List[str] = 'HS256'
  key: str | bytes | None = None
  operation: str | None = None
  payload: dict | None = None
  token: str | None = None


@dc.dataclass
class Header:
  algorithm: str = 'HS256'
  type: str = 'JWT'


@dc.dataclass
class Payload:
  issuer: str | None = None
  subject: str | None = None
  audience: str | None = None
  expiration_time: int | None = None
  not_before: int = dc.field(default_factory=lambda: int(time.time()))
  issued_at: int = dc.field(default_factory=lambda: int(time.time()))
  jwt_id: str | None = None
  content: Any | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  call_method: str = 'module'
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
  if dc.is_dataclass(data.body.payload):
    data.body.payload = dc.asdict(data.body.payload)

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
    jwt=data.body.token,
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
  key = getattr(ENV, key_name)
  data.body.key = key if not data.body.key else data.body.key
  data.body.key = await format_key(key=data.body.key)
  switcher = PERFORM_OPERATION[data.body.operation]
  data = await switcher(data=data)
  return data


async def get_jwt_as_response(data: Data) -> dict:
  data = {'token': data.result}
  return data


async def get_payload_as_response(data: Data) -> dict:
  data = {'payload': data.result}
  return data


async def get_jwt_as_string(data: Data) -> str:
  return {'token': data.result}


async def get_payload_as_data_class(data: Data) -> Payload:
  store = []
  for key, value in data.result.items():
    value = json.dumps(value)
    field_value = dc.field(default=value)
    data_classfield = [
      key,
      str,
      field_value,
    ]
    store.append(data_classfield)
  data_class = dc.make_dataclass(
    cls_name='Payload',
    fields=store,
  )
  data_class = data_class()
  return data_class


GET_RESPONSE = {
  'api.encode': get_jwt_as_response,
  'api.decode': get_payload_as_response,
  'module.encode': get_jwt_as_string,
  'module.decode': get_payload_as_data_class,
}


async def get_response(data: Data) -> dict | str | Payload:
  cases = f'{data.call_method}.{data.body.operation}'
  switcher = GET_RESPONSE[cases]
  data = await switcher(data=data)
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  algorithm: str | None = None,
  key: str | bytes | None = None,
  payload: dict | Payload | None = None,
  header: dict | Header = None,
  token: Any | None = None,
  operation: Any | None = None,
) -> Payload | dict | str:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await preform_operation(data=data)
  data = await get_response(data=data)
  return data

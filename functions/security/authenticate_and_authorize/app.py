#!/usr/bin/env python3

import dataclasses as dc
from typing import List
# import time
import json
from fastapi import Request, HTTPException

from shared.format_main_arguments import app as format_main_arguments
from functions.security.jwt import app as security_jwt
from functions.utilities.query_db import app as query_db
from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Headers:
  authorization: str | None = None
  user_agent: str | None = None
  origin: str | None = None


@dc.dataclass
class Body:
  authenticate: bool = True
  required_roles: List[str] | None = None
  authentication_type: str = 'Bearer'
  token_type: str = 'jwt'


@dc.dataclass
class Token:
  value: str | None = None
  payload: security_jwt.Payload | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  headers: Headers | None = None
  token: Token | None = None
  user: 'User | None' = None
  client: 'Client | None' = None
  authenticated: bool = False
  authorized: bool = False
  call_method: str = 'module'


@dc.dataclass
class DataClass:
  # Generic dataclass type hint
  ...


async def process_request_attribute(
  request: Request,
  attribute: str,
  data_class: DataClass,
) -> Data:
  data = data_class()

  if not hasattr(request.data, attribute):
    return data

  attribute = getattr(request.data, attribute)

  for field in dc.fields(data):
    if not hasattr(attribute, field.name):
      continue
    value = getattr(attribute, field.name)
    if value is None:
      continue
    setattr(data, field.name, value)
  return data


async def get_jwt_token_and_payload(data: Data) -> Data:
  token = data.headers.authorization
  if not token:
    raise HTTPException(
      status_code=401,
      detail='no authorization header',
    )
  
  token = token.replace(data.body.authentication_type, '')
  token = token.strip()
  payload = await security_jwt.main(
    token=token,
    operation='decode',
  )
  data.token = Token(value=token, payload=payload)
  return data


TOKEN_TYPE = {
  'jwt': get_jwt_token_and_payload,
}


async def get_token_and_payload(data: Data) -> Data:
  if not hasattr(data.headers, 'authorization'):
    raise HTTPException(
      status_code=401,
      detail='no authorization header',
    )
  function = TOKEN_TYPE[data.body.token_type]
  data = await function(data=data)
  return data


async def authenticate_user(data: Data) -> Data:
  if data.body.authenticate is False:
    return data

  print('TODO - ADD AUTHENTICATE USER LOGIC')
  # Check if JWT is expired. Issue new one if so
  # encryption key

  return data


async def authorize_user(data: Data) -> Data:
  if data.body.required_roles in [[], None]:
    data.authorized = True
    return data

  roles = await query_db.main(
    database='dynamodb',
    query='get_a_users_role',
    parameters={'user_id': data.user.id},
  )
  data.user.roles = roles[0]
  for role in data.user.roles:
    if role in data.body.required_roles:
      data.authorized = True
      return data

  status_code = 403
  if data.authenticated is True:
    status_code = 401
  raise HTTPException(
    status_code=status_code,
    detail='unauthorized',
  )

async def get_response(data: Data) -> Data:
  if data.call_method == 'api':
    data.user = dc.asdict(data.user)
  data = {
    'user': data.user,
    'token': data.token.value,
  }
  return data


async def format_payload_content(data: Data) -> Data:
  content = json.loads(data.token.payload.content)

  for content_key, content_value in content.items():
    fields = []
    for key, value in content_value.items():
      field = [
        key,
        str,
        dc.field(default=value),
      ]
      fields.append(field)
    cls_name = content_key.title()
    data_class = dc.make_dataclass(cls_name=cls_name, fields=fields)
    setattr(data, content_key, data_class())

  data.token.payload.content = None
  return data


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  authenticate: bool | None = None,
  required_roles: List[str] | None = None,
  authentication_type: str | None = None,
  token_type: str | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body, 'headers': Headers},
    main_data_class=Data,
  )
  data = await get_token_and_payload(data=data)
  data = await format_payload_content(data=data)
  data = await authenticate_user(data=data)
  data = await authorize_user(data=data)
  data = await get_response(data=data)
  return data

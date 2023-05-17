#!/usr/bin/env python3

from dataclasses import dataclass, field, asdict, fields
from typing import List
import time

from api import models as api_models
# import functions.security.jwt.app as security_jwt
from functions.security.jwt import app as security_jwt


# Set Token type and algorithm in environment


@dataclass
class RequestData:
  ...


@dataclass
class Headers(api_models.Headers):
  authorization: str | None = None
  # TODO: Hash these to identify if user is using a new device
  user_agent: str | None = None
  origin: str | None = None


@dataclass
class Body:
  authenticate: bool = True
  token_type: str = 'jwt'
  authenticate: bool = True


@dataclass
class User(api_models.User):
  ...


@dataclass
class Data:
  body: Body | None = None
  headers: Headers | None = None
  user: dict | User | None = None
  payload: security_jwt.Payload | None = None


async def process_request_headers(request_headers: api_models.Headers) -> Headers:
  headers = Headers()
  for _field in fields(headers):
    if not hasattr(request_headers, _field.name):
      continue
    value = getattr(request_headers, _field.name)
    if value is None:
      continue
    setattr(headers, _field.name, value)
  return headers


async def process_request_body(request_body: api_models.Body) -> RequestData:
  body = Body()
  for _field in fields(body):
    if not hasattr(request_body, _field.name):
      continue
    value = getattr(request_body, _field.name)
    if value is None:
      continue
    setattr(body, _field.name, value)

  return body


async def process_request_arg(_locals: dict) -> Data:
  headers = await process_request_headers(
    request_headers=_locals['request'].data.headers)
  body = await process_request_body(
    request_body=_locals['request'].data.body)
  data = Data(body=body, headers=headers)
  return data


async def process_non_request_args(_locals: dict) -> Data:
  ignore_keys = ['request']
  data = Data()
  for key, value in _locals.items():
    if value is None or key in ignore_keys:
      continue
    setattr(data, key, value)
  return data


PROCESS_MAIN_ARGS = {
  'request': process_request_arg,
  'non_request': process_non_request_args,
}


async def process_main_args(_locals: dict) -> Data:
  cases = 'request' if _locals['request'] else 'non_request'
  switcher = PROCESS_MAIN_ARGS[cases]
  data = await switcher(_locals=_locals)
  return data


async def get_jwt_when_no_header_authorization(data: Data) -> Data:
  '''Create a JWT for an anonymous user when Authorization header does
  not exist'''
  if data.headers.authorization:
    return data
  # Delete me. This should query db instead
  import yaml
  content = '''
    client:
      user_agent: null
      origin: null
    user:
      id: user_00
      roles:
      - anonymous
      email: user@email.come
      name: first_name, last_name
  '''
  content = yaml.safe_load(content)
  payload = security_jwt.Payload(content=content)
  data.token = await security_jwt.main(payload=payload, operation='encode')
  return data


async def get_payload_from_jwt(data: Data) -> Data:
  jwt = data.headers.authorization.split(' ')[-1]
  payload = await security_jwt.main(jwt=jwt, operation='decode')
  data.payload = payload()
  return data


async def get_client_and_user_information(data: Data) -> Data:
  data = await get_jwt_when_no_header_authorization(data=data)
  data = await get_payload_from_jwt(data=data)
  return data


async def authenticate_user(data: Data) -> Data:
  if data.body.authenticate is False:
    return data

  steps = '''
  resources:
  - url: https://stackoverflow.blog/2021/10/06/best-practices-for-authentication-and-authorization-for-rest-apis/
  - url: https://security.stackexchange.com/questions/119371/is-refreshing-an-expired-jwt-token-a-good-strategy
  - Query authenticated users table
  - If user is not in authenticated table they 
    are anonymous and should be asked to register
  - If user in authenticated table 
  - user signs in and is issued a refresh token
  - check if JWT is expired, if so sign in again
    and issue new jwt
    - check that client user agent and origin have been used, if not sign in again
    - refresh token every 15 minutes
  Check if role contains anonymous
  '''

  return data


async def get_cookie(data: Data) -> Data:

  return data


# pylint: disable=unused-argument
async def main(
  request: api_models.Request | None = None,
  headers: Headers | None = None,
  user: User | None = None,
  authenticate: bool | None = None,
  token: str | None = None,
  token_type: str | None = None,
) -> User | api_models.Response:
  data = await process_main_args(_locals=locals())
  data = await get_client_and_user_information(data=data)
  print(data)
  data = await authenticate_user(data=data)
  data = await get_cookie(data=data)
  return api_models.Response()


security = '''
  users:
    anonymous: allow
    authenticated: allow
    authorized:
    - anonymous
    - authenticated
'''


def decorator_factory(
  authenticate: bool = True,
  allow: List[str] = ['anonymous'],
) -> api_models.Response | api_models.Error:
  print(locals())
  def decorator(function):
    async def wrapper(*args, **kwargs):
      print(args, kwargs['request'].data.headers)
      result = await function(*args, **kwargs)
      return result
    return wrapper
  return decorator

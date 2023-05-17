#!usr/bin/env python3

from dataclasses import dataclass
from typing import Any


@dataclass
class DataClass:
  ...


@dataclass
class User():
  ...


@dataclass
class Env:
  ...


@dataclass
class Headers:
  ...


@dataclass
class PathParams:
  function_path: str | None = None


@dataclass
class QueryParams:
  ...


@dataclass
class Body:
  ...


@dataclass
class JSON:
  ...


@dataclass
class Binary:
  ...


@dataclass
class Form:
  ...


@dataclass
class Data:
  method: str | None = None
  headers: Headers | None = None
  path_params: PathParams | None = None
  query_params: QueryParams | None = None
  body: Body | None = None
  form: Form | None = None


@dataclass
class Request:
  data: Data | None = None


@dataclass
class Response:
  code: int = 200
  status: str = 'OK'
  data: Any | None = None


@dataclass
class Error:
  code: int = 500
  message: str = 'Internal Server Error'


# pylint: disable=unused-argument
# async def get_response(
#   code: int | None = None,
#   status: str | None = None,
#   data: Any | None = None,
# ) -> Response:
#   response = Response()
#   for key, value in locals().items():
#     if value is None:
#       continue
#     setattr(response, key, value)
#   return response

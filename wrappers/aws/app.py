#!/usr/bin/env python3

from typing import Any, List, Dict
from dataclasses import dataclass, fields
from copy import deepcopy
import boto3

from shared.get_environment import app as get_environment
from shared.setup_data import app as setup_data
# from shared.error_handler import app as error_handler
from api import models as api_models


ENV = get_environment.main({'module_path': __file__})
SESSION_CACHE = None
CLIENT_CACHE = {}


@dataclass
class Body(api_models.Body):
  ...


@dataclass
class Data:
  service_name: str | None = None
  service_params: Any | None = None
  request_response: Any | None = None
  parse_response: List[str] | str | None = None


# pylint: disable=fixme
# TODO: Move to setup_data module
def process_local_arguments(
  _locals: Dict[str, Any],
  data_class: 'DataClass',
) -> Data:
  if _locals['data'] is not None:
    return _locals['data']

  data = data_class()
  for _field in fields(data):
    if _field.name not in _locals:
      continue
    setattr(data, _field.name, _locals[_field.name])
  return data


def get_session(data: None = None) -> 'boto3.session':
  _ = data
  session = boto3.session.Session(
    aws_access_key_id=ENV.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=ENV.AWS_SECRET_ACCESS_KEY,
    region_name=ENV.AWS_REGION_NAME,
  )
  return session


def get_session_from_cache(data: None = None) -> 'boto3.session':
  _ = data
  # pylint: disable=global-statement
  global SESSION_CACHE
  # Add session to cache
  if SESSION_CACHE is None:
    SESSION_CACHE = get_session(None)
  return SESSION_CACHE


def get_client(service_name: str) -> 'botocore.client':
  session = get_session_from_cache()
  client = session.client(service_name=service_name)
  return client


def get_client_from_cache(
  service_name: str,
) -> 'botocore.client':
  # pylint: disable=global-variable-not-assigned
  global CLIENT_CACHE
  service_name = service_name.lower()
  if service_name not in CLIENT_CACHE:
    CLIENT_CACHE[service_name] = get_client(
      service_name=service_name)
  return CLIENT_CACHE[service_name]


def get_request(service_name: str) -> 'method | botocore.client':
  names = service_name.lower().split('.')
  service_name = names[0]
  request = get_client_from_cache(service_name=service_name)
  names_range = range(1, len(names))
  for i in names_range:
    request = getattr(request, names[i])
  return request


GET_RESPONSE = {
  0: lambda request, params: request(),
  1: lambda request, params: request(params),
  2: lambda request, params: request(*params),
  3: lambda request, params: request(**params),
  4: lambda request, params: request,
}


def get_response(
  service_name: str,
  service_params: Any | None = None,
) -> Any:
  request = get_request(service_name=service_name)

  params_type = type(service_params).__name__
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
    params=service_params,
    request=request,
  )
  return response


def process_response_list(
  key: str,
  parsed_response: List[Any],
) -> List[Any]:
  store = []
  for response in parsed_response:
    value = response[key]
    store.append(value)
  return store


PROCESS_RESPONSE = {
  'list': process_response_list,
  'dict': lambda key, parsed_response: parsed_response[key],
}


def process_response(
  response: Dict,
  parse_response: List[str] | str | None = None,
) -> Any:
  if parse_response in [None, []]:
    return response

  if isinstance(parse_response, list) is False:
    parse_response = [parse_response]

  store = []
  for parse in parse_response:
    parsed_response = deepcopy(response)
    keys = parse.split('.')
    for key in keys:
      parsed_response_type = type(parsed_response).__name__
      function = PROCESS_RESPONSE[parsed_response_type]
      parsed_response = function(
        key=key,
        parsed_response=parsed_response,
      )
    store.append(parsed_response)
  # Return a single item or multiple items
  if len(store) == 1:
    return store[0]
  return store


# @error_handler.main()
def main(
  data: Data | dict | str | None = None,
  service_name: str | None = None,
  service_params: Any | None = None,
) -> Any:
  data = setup_data.main(data=data, data_class=Data)
  data = process_local_arguments(
    _locals=locals(), data_class=Data)
  _ = service_name, service_params
  response = get_response(
    service_name=data.service_name,
    service_params=data.service_params,
  )
  data.request_response = process_response(
    response=response,
    parse_response=data.parse_response,
  )
  return data


def example() -> None:
  from shared.execute_example_data import app as execute_example_data


  examples = [
    '''
    service_name: s3.list_buckets
    service_params: null
    parse_response: 
    # - Buckets
    - Buckets.Name
    - Buckets.CreationDate
    ''',
    '''
    service_name: s3.list_objects
    service_params:
      Bucket: ${S3_BUCKET}
    parse_response:
    # - Contents
    - Contents.Key
    ''',
    '''
    service_name: s3.put_object
    service_params:
      Bucket: ${S3_BUCKET}
      Bucket: oj-aws-s3-bucket-01
      Body: '{"test": "test"}'
      Key: test_000
    parse_response:
    - ResponseMetadata.HTTPStatusCode
    ''',
    '''
    service_name: s3.create_bucket
    service_params:
      Bucket: helloworld04232021
    parse_response:
    - ResponseMetadata.HTTPHeaders.location
    ''',
    '''
    service_name: s3.delete_bucket
    service_params: 
      Bucket: helloworld04232021
    parse_response:
    - ResponseMetadata.HTTPStatusCode
    ''',
    '''
    service_name: lambda.list_functions
    service_params: null
    parse_response: Functions
    ''',
  ]
  execute_example_data.main(
    examples=examples,
    main_function=main,
  )


if __name__ == '__main__':
  example()

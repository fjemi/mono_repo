#!/usr/bin/env python3

import dataclasses as dc
from typing import Dict, List
import os
import glob
from fastapi import FastAPI

import yaml
from shared.get_environment import app as get_environment


THIS_MODULE_PATH = __file__
SCHEMA_FILE_SUFFIX = '_openapi.yml'
ENV = get_environment.main(module_path=THIS_MODULE_PATH)


@dc.dataclass
class Data:
  working_directory: str = ENV.WORKDIR
  schema_file_suffix: str = SCHEMA_FILE_SUFFIX
  app_module_path: str | None = None
  directories: List[str] = dc.field(default_factory=lambda: ['functions'])
  app_schema: dict | None = None
  route_schemas: Dict[str, dict] | None = None
  app: FastAPI | None = None


@dc.dataclass
class Output:
  app: FastAPI | None = None
  schema: dict | None = None
  routes: List[str] | None = None


def initialize_dataclass(_locals: dict) -> Data:
  '''Initializes a dataclass with non-null keyword arguments passed into 
  the main function'''
  data = Data()
  for key, value in _locals.items():
    if value is None:
      continue
    setattr(data, key, value)
  return data


def get_app_schema(data: Data) -> Data:
  '''Returns the OpenAPI schema for the API'''
  schema_path = data.app_module_path.replace('.py', data.schema_file_suffix)
  schema = None
  with open(schema_path, 'r', encoding='utf-8') as file:
    schema = file.read()
  schema = os.path.expandvars(schema)
  schema = yaml.safe_load(schema)
  data.app_schema = schema if schema else {}
  return data


def get_schema_paths_from_directories(
  data: Data,
) -> Dict[str, List[str]]:
  '''Returns OpenAPI schema files within a list of directories'''
  if not data.directories:
    data.directories = ['']
  if isinstance(data.directories, str):
    data.directories = [data.directories]

  store = {}
  for directory in data.directories:
    directory_path = os.path.join(data.working_directory, directory)
    match = f'{directory_path}/**/*{data.schema_file_suffix}'
    store[directory] = glob.glob(match, recursive=True)
  return store


def get_routes_from_schema_paths(
  schema_paths: Dict[str, str],
) -> Data:
  '''Returns the name for a route associated with an OpenAPI schema file.
  The name is the dot-delimited path from the working directory to the file.
  '''
  store = {}
  for directory, file_paths in schema_paths.items():
    for file_path in file_paths:
      if file_path.find('ignore') != -1:
        continue
      i = file_path.find(directory)
      route = file_path[i:]
      route = route.split(os.sep)
      route = '.'.join(route[:-1])
      store[route] = file_path
  return store


def get_schemas_for_routes(
  schema_paths: Dict[str, str],
) -> Dict[str, dict]:
  '''Returns a dictionary with keys as dot delimited API routes and values
  as OpenAPI schemas load from file paths'''
  store = {}

  # Sort routes so that they appear in order in Swagger UI
  routes = list(schema_paths.keys())
  routes.sort()

  for route in routes:
    path = schema_paths[route]

  # for route, path in schema_paths.items():
    schema = None
    with open(path, 'r', encoding='utf-8') as file:
      schema = file.read()
    # Set the function path for the schema
    schema = schema.replace('{path}', route)
    schema = os.path.expandvars(schema)
    schema = yaml.safe_load(schema)
    store[route] = schema if schema else {}
  return store


def get_route_schemas(data: Data) -> Data:
  '''Sets the API routes for functions and loads their OpenAPI schema'''
  schema_paths = get_schema_paths_from_directories(data=data)
  schema_paths = get_routes_from_schema_paths(schema_paths=schema_paths)
  data.route_schemas = get_schemas_for_routes(schema_paths=schema_paths)
  return data


def add_route_schema_paths_to_app_schema(
  app_schema: dict,
  route_schema: dict,
) -> dict:
  '''Adds path objects defining GET and/or POST methods for routes to the 
  app schema'''
  key = 'paths'
  if key not in app_schema:
    app_schema[key] = {}
  for path, schema in route_schema[key].items():
    app_schema[key][path] = schema
  return app_schema


def add_route_schema_tags_to_app_schema(
  app_schema: dict,
  route_schema: dict,
) -> dict:
  key = 'tags'
  if key not in app_schema:
    app_schema[key] = []
  for tag in route_schema[key]:
    if tag in app_schema[key]:
      continue
    app_schema[key].append(tag)
  return app_schema


def add_route_schema_components_to_app_schema(
  app_schema: dict,
  route_schema: dict,
) -> dict:
  key = 'components'
  if key not in app_schema:
    app_schema[key] = {}
  if key in route_schema:
    for subsection, info in route_schema[key].items():
      if subsection not in app_schema[key]:
        app_schema[key][subsection] = {}
      for info_key, info_value in info.items():
        app_schema[key][subsection][info_key] = info_value
  return app_schema


KEY_SWITCHER = {
  'paths': add_route_schema_paths_to_app_schema,
  'tags': add_route_schema_tags_to_app_schema,
  'components': add_route_schema_components_to_app_schema,
  'security': ...,
}


def combine_app_and_route_schemas(data: Data) -> Data:
  '''Adds OpenAPI objects for route schemas to the app schema'''
  for route_schema in data.route_schemas.values():
    for key in route_schema:
      switcher = KEY_SWITCHER[key]
      data.app_schema = switcher(
        app_schema=data.app_schema,
        route_schema=route_schema,
      )
  return data


def set_app_schema_and_get_routes(data: Data) -> Data:
  if not data.app_schema and data.app:
    data.app_schema = data.app.openapi_schema

  if data.app:
    data.app.openapi_schema = data.app_schema
  routes = []

  key = 'paths'
  if key in data.app_schema:
    routes = list(data.app_schema[key].keys())
  routes.sort()

  output = Output(
    app=data.app,
    schema=data.app_schema,
    routes=routes,
  )
  return output


# pylint: disable=unused-argument
def main(
  app_module_path: str | None = None,
  working_directory: str | None = None,
  directories: List[str] | None = None,
  schema_file_suffix: str | None = None,
  app: FastAPI | None = None,
) -> dict | FastAPI:
  '''Orchestration function'''
  data = initialize_dataclass(_locals=locals())
  data = get_app_schema(data=data)
  data = get_route_schemas(data=data)
  data = combine_app_and_route_schemas(data)
  data = set_app_schema_and_get_routes(data=data)
  return data


def example() -> None:
  THIS_DIRECTORY = os.path.dirname(THIS_MODULE_PATH)
  TEST_RESOURCES_APP_MODULE_PATH = os.path.join(
    THIS_DIRECTORY,
    'test_resources',
    'app.py',
  )
  test_resources_function_directory = os.path.join(
    THIS_DIRECTORY,
    'test_resources',
    'functions',
  )
  result = main(
    app_module_path=TEST_RESOURCES_APP_MODULE_PATH,
    directories=test_resources_function_directory,
  )
  print(result)


if __name__ == '__main__':
  example()

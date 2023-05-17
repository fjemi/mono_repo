#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Any
import fastapi

from shared.get_environment import app as get_environment
from shared.setup_data import app as setup_data
from shared.error_handler import app as error_handler


ENV = get_environment.main({'module_path': __file__})


class Cache:
  pass

CACHE = Cache()


@dataclass
class Data:
  object_name: str | None = None
  object_params: Any | None = None
  instantiate: bool = False


def get_object(object_name: str) -> Any:
  ...
  

def main(data: Data) -> Data:
  data = setup_data.main(data=data)
  return 


if __name__ == '__main__':
  app = fastapi.FastAPI()
  print([
    dir(fastapi),
    type(fastapi),
    type(app),
    # dir(app),
  ])




# from dataclasses import dataclass, fields
# from typing import Any, Dict, Callable
# from types import ModuleType
# from fastapi import FastAPI
# import dacite


# @dataclass
# class Data:
#   root: ModuleType | Callable | None = None
#   import_root: bool = False
#   object_name: str | None = None
#   params: Dict[str | int,  Any] | None = None
#   call_object: bool = True
#   result: Any | None = None
  
  
# def pre_processing(
#   root: ModuleType | Callable | None | str = None,
#   import_root: bool = False,
#   object_name: str = None,
#   params: Dict[str | int, Any] | None = None,
#   call_object: bool = True,
# ) -> Data | None:
#   if root is None:
#     return None
  
#   data = dacite.from_dict(Data, locals())
#   return data
  
  
  
  
# def main(
#   root: ModuleType | Callable | None | str = None,
#   import_root: bool = False,
#   object_name: str = None,
#   params: Dict[str | int, Any] | None = None,
#   call_object: bool = True
# ) -> Any:
#   data = pre_processing(
#     root=root,
#     object_name=object_name,
#     params=params,
#     call_object=call_object,
#   )
#   return data


# # app = FastAPI()


# # @app.get('/')
# # def root():
# #   return dict(hello='world')
  
  
# # def run_server() -> bool:
  
  
# #   return True


# def example() -> None:
#   data = main(
#     root=FastAPI,
#     call_object=False,
#   )
#   print(data)
  
#   # run_server()
  
  
# if __name__ == '__main__':
#   example()


def get_app(data: dict = {}) -> Any:
  global CACHE
  if hasattr(CACHE, 'app') is True:
    return CACHE.app
  if 'api' in data.keys():
    CACHE.app = fastapi.FastAPI(**data['api'])
  else:
    CACHE.app = fastapi.FastAPI()
  return CACHE.app


def get_router(data: dict = {}) -> Any:
  global CACHE
  if hasattr(CACHE, 'router') is True:
    return CACHE.router
  CACHE.router = fastapi.APIRouter(**data)
  return CACHE.router

app = get_app()
print(app)
print(type(app).__name__)
from fastapi import applications
# print(dir(applications.routing.APIRouter))
# print(dir(applications))
print(dir(fastapi.FastAPI()).sort())
# print(dir(fastapi.FastAPI().on_event(event_type='/test')))
test = applications.routing.APIRouter == fastapi.APIRouter
print(test)

from inspect import signature
_object = fastapi.FastAPI().on_event
object_signature = signature(_object)
print(object_signature, _object, dir(_object))


yaml_data = '''
  api:
    title: API Wrapper
    description: A Wrapper over FastAPI
    version: 0.0.1
    on_event:
      event_type: 
'''

import yaml
yaml_data = yaml.safe_load(yaml_data)

app = get_app(data=yaml_data)
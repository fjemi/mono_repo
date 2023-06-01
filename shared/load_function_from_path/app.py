#!/usr/bin/env python3

import dataclasses as dc
from os import path
from importlib.machinery import SourceFileLoader
from typing import Callable, Any
from fastapi import Request

from shared.get_environment import app as get_environment
from shared.format_main_arguments import app as format_main_arguments


THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)


@dc.dataclass
class Function:
  name: str = 'main'
  module: str = 'app.py'
  directory: str = 'functions.hello_world'
  module_path: str | None = None
  function: Callable | None = None


@dc.dataclass
class Body:
  function: dict | Function  = None
  import_module_path: str | None = None
  working_directory: str = ENV.WORKDIR


@dc.dataclass
class Data:
  body: Body | None = None
  call_method: str = 'module'
  response: Any | None = None


async def get_function_module_path(data: Data) -> str:
  directory = data.body.working_directory
  if data.body.import_module_path:
    directory = path.dirname(data.body.import_module_path)

  folders = data.body.function.directory.split('.')
  for folder in folders:
    directory = path.join(directory, folder)
  module_path = path.join(directory, data.body.function.module)
  return module_path


async def load_function_from_module_path(
  function: Function,
) -> Function:
  parent_folder = function.directory.split('-')[-1]
  module = SourceFileLoader(
    parent_folder,
    function.module_path,
  ).load_module()
  function = getattr(module, function.name)
  return function


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  function: dict | Function  = None,
  import_module_path: str | None = None,
  working_directory: str | None = None,
) -> Callable:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  data.body.function = Function(**data.body.function)
  data.body.function.module_path = await get_function_module_path(data=data)
  data.response = await load_function_from_module_path(
    function=data.body.function)
  return data.response


async def example() -> None:
  import yaml


  data = f'''
    function:
      name: main
      module: app.py
      directory: test_resources
    import_module_path: {THIS_MODULE_PATH}
  '''
  data = yaml.safe_load(data)
  result = await main(**data)
  print(result)


if __name__ == '__main__':
  import asyncio


  asyncio.run(example())

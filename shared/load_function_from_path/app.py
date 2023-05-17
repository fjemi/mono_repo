#!/usr/bin/env python3

from dataclasses import dataclass, field
from os import path
from importlib.machinery import SourceFileLoader
from typing import Callable

from api import models
from shared.get_environment import app as get_environment
from shared.setup_data import app as setup_data


THIS_MODULE_PATH = __file__
ENV = get_environment.main(data=f'module_path: {__file__}')


@dataclass
class Function:
  name: str = 'main'
  module: str = 'app.py'
  directory: str = 'functions.hello_world'
  module_path: str | None = None
  function: Callable | None = None


@dataclass
class Data:
  function: Function  = None
  import_module_path: str | None = None
  env: models.Env = field(default_factory=lambda: ENV)


async def get_function_module_path(data: Data) -> str:
  directory = data.env.WORKDIR
  if data.import_module_path:
    directory = path.dirname(data.import_module_path)
    
  folders = data.function.directory.split('.')
  for folder in folders:
    directory = path.join(directory, folder)
  module_path = path.join(directory, data.function.module)
  return module_path


async def load_function_from_module_path(
  function: Function,
) -> Function:
  parent_folder = function.directory.split('-')[-1]
  module = SourceFileLoader(
    parent_folder,
    function.module_path,
  ).load_module()
  function.function = getattr(module, function.name)
  return function


async def main(data: Data | dict | str) -> 'Callable':
  data = setup_data.main(data=data, data_class=Data)
  data.function.module_path = await get_function_module_path(data=data)
  data.function = await load_function_from_module_path(function=data.function)
  return data.function.function


async def example() -> None:
  data = f'''
    function:
      name: main
      module: app.py
      directory: test_resources
    import_module_path: {__file__}
  '''
  result = await main(data=data)
  print(result)
  

if __name__ == '__main__':
  import asyncio
  
  
  asyncio.run(example())

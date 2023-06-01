#!usr/bin/env python3

import dataclasses as dc
import glob
import os
from typing import Dict, List
from runpy import run_path

from shared.get_environment import app as get_environment


THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)


@dc.dataclass
class Data:
  app_module_path: str | None = None
  operations_directory: str = 'operations'


async def get_module_paths_for_operations(
  app_module_path: str,
) -> List[str]:
  directory = os.path.dirname(app_module_path)
  directory = os.path.join(directory, 'operations')
  match = f'{directory}/**/*app.py'
  module_paths = glob.glob(match, recursive=True)
  return module_paths


async def get_main_functions_from_modules(
  module_paths: List[str],
) -> Dict[str, Dict[str, str]]:
  store = {}
  for path in module_paths:
    module = run_path(path)
    store[path] = module['main']
  return store


async def get_subjects_operations_and_routes(
  module_paths: List[str],
) -> Dict[str, Dict[str, str]]:
  store = {}
  for key in module_paths:
    index = key.find('functions')
    key = key[index:]
    key = key.split(os.sep)
    subject, operation = key[-3:-1]
    key = '.'.join(key)
    if subject not in store:
      store[subject] = []
    store[subject].append({'name': operation, 'route': key})
  return store


async def main(app_module_path: str) -> Dict[str, Dict[str, str]]:
  module_paths = await get_module_paths_for_operations(
    app_module_path=app_module_path)
  routes = await get_subjects_operations_and_routes(
    module_paths=module_paths)
  
  store = ''
  for subject in routes:
    subject = f'<ul>{subject}</ul>'

  return routes


if __name__ == '__main__':
  import asyncio


  app_module_path = '/functions/coding_challenges/calculator/app.py'
  app_module_path = ENV.WORKDIR + app_module_path
  result = asyncio.run(main(app_module_path=app_module_path))
  print(result)

  # function = result ['absolute_value']
  # result = asyncio.run(function(inputs=1, operation='absolute_value'))
  # print(result)

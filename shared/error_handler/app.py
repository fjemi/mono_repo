#!/usr/bin/env python3

from dataclasses import dataclass, asdict
from typing import Any, List, Dict
import time
import traceback
import json
from copy import deepcopy
import yaml

from shared.get_environment import app as get_environment
from shared.logger import app as logger


ENV = get_environment.main(f'module_path: {__file__}')


@dataclass
class RunTime:
  start: int = 0
  end: int = 0
  total_ms: float = 0.0


@dataclass
class Error:
  _type: str | None = None
  description: str | None = None
  _traceback: str | None = None


@dataclass
class Data:
  function_name: str | None = None
  module_path: str | None = None
  args: List[Any] | str | None = None
  kwargs: Dict[str, Any] | str | None = None
  result: Any | None = None
  error: Error | None = None
  run_time: RunTime | None = None
  
  
def process_module_path(
  module_path: str | None = None,
  working_dir: str = ENV.WORKDIR,
) -> str:
  if module_path is None:
    return ''
  return module_path.replace(working_dir, '')


def pre_processing(_locals: Dict) -> Data:
  start = time.time()
  run_time = RunTime(start=start)
  args = deepcopy(list(_locals['args']))
  kwargs = deepcopy(_locals['kwargs'])
  function_name = _locals['function'].__name__
  module_path = process_module_path(module_path=_locals['module_path'])
  data = Data(
    run_time=run_time,
    function_name=function_name,
    module_path=module_path,
    args=args,
    kwargs=kwargs,
  )
  return data


def process_error(error: Exception) -> Error:
  _traceback = traceback.format_exc().split('\n')[:-2]
  error = Error(
    _type = error.__class__.__name__,
    description=error.args[0],
    # _traceback=traceback.format_exc(),
    _traceback=_traceback
  )
  return error


def process_run_time(run_time: RunTime) -> RunTime:
  run_time.end = time.time()
  total = run_time.end - run_time.start
  run_time.total_ms = total * 1000
  return run_time


def post_processing(_locals: Dict) -> Data:
  data = _locals['data']
  data.run_time = process_run_time(run_time=data.run_time)
  return data


#TODO: Move functionality to logger
def log_data(
  data: Data | Any,
  debug: bool = ENV.DEBUG,
  module_path: str | None = None,
  message: str | None = None,
  log_format: str = 'json',
  log: bool = True,
) -> None:
  if log is False:
    return
  
  level = 'INFO'
  if data.error is not None:
    level = 'ERROR'

  if hasattr(data, '__dataclass_fields__') is True:
    data = asdict(data)
    

  try:
    _ = json.dumps(data)
  except:
    
    # Convert fields to strings
    convert_fields = ['result', 'args', 'kwargs']
    for _field in convert_fields:
      value = data[_field]
      data[_field] = str(value)

  if str(debug) == 'True':
    data = {'log': data}
    data = yaml.dump(
      data,
      default_flow_style=None,
    )
    print(data)
  else:
    data = json.dumps(data)
  logger.main(
    data=data,
    level=level,
    module_path=module_path,
  )


def main(
  debug: bool = ENV.DEBUG,
  raise_error: bool = False,
  return_value: Any = None,
  message: str | None = None,
  module_path: str | None = None,
  log_format: str = 'json',
  log: bool = True,
) -> Any:
  def error_handler(function):
    def wrapper(*args, **kwargs):
      data = pre_processing(_locals=locals())

      # Execute function with args
      try:
        data.result = function(*args, **kwargs)
      except Exception as error:
        data.error = process_error(error=error)
        data.result = return_value

      data = post_processing(_locals=locals())
      log_data(
        log=log,
        data=data,
        debug=debug,
        module_path=module_path,
      )
      return data.result
    return wrapper
  return error_handler


def example() -> None:
  @dataclass
  class Nums:
    a: int = 0
    b: int = 0
    result: int = 0


  @main(
    debug=True,
    return_value='return_value_0',
    module_path=__file__,
    log_format='json',
  )
  def add(a: int, b: int) -> int:
    return a + b


  @main(
    debug=True,
    return_value='return_value_1',
    module_path=__file__,
    log_format='yaml',
  )
  def subtract(data: Nums) -> Nums:
    data.result = data.b - data.a
    return data


  data = [
    subtract(Nums(1, 2)), 
    subtract(data=Nums()), 
    add(a=1, b=2),
    add(a='1', b=2), 
    subtract(data=None),
  ]
  print(data)


if __name__ == '__main__':
  example()

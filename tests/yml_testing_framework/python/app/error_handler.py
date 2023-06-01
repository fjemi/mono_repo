# 

from typing import Callable, Any, List, Dict, Tuple
import dataclasses as dc
import yaml
import time

from shared.get_environment import app as get_environment


THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)



@dc.dataclass
class Time:
  start: float = None
  end: float = None
  run: str = None


@dc.dataclass
class Log:
  function: str = None
  args: List | Tuple = None
  kwargs: Dict = None
  result: Any = None
  _time: Time = dc.field(default_factory=lambda: Time())
  memory_usage: float = None
  error: str = None


@dc.dataclass
class Data:
  log_path: str | None = ''


def format_time(_time: Time) -> Time:
  _time.end = time.time()
  # Set run time
  _time.run = _time.end - _time.start
  _time.run = f'{_time.run * 1000} ms'
  # format start/end time
  _time.start = time.ctime(_time.start)
  _time.end = time.ctime(_time.end)
  return _time


def format_log(log: Log, result: Any) -> Log:
  log._time = format_time(_time=log._time)
  log.result = str(result)
  log = dc.asdict(log)
  log = yaml.dump(dict(log=log), indent=2)
  return log


def error_handler(function: Callable, *args, **kwargs) -> Any:
  log = Log(
    function=f'{function.__module__}.{function.__name__}',
    args=str(args),
    kwargs=str(kwargs),
    _time=Time(start=time.time()),
  )

  result = None
  try:
    result = function(*args, **kwargs)
    log.result = result
  except Exception as e:
    log.error = str(e)

  # log = format_log(log=log, result=result)
  # print(log)
  return log
  return result


def add(a, b):
  return a + b


data = error_handler(function=add, a=1, b=1)
print(data)


def decorator_factory(debug: bool = ENV.DEBUG):
  pass


def main(function: Callable) -> Any:
  def wrapper(*args, **kwargs) -> Any:
    # result = error_handler(
    #   function=function, 
    #   args=args, 
    #   kwargs=kwargs,
    # )
    # result = dc.asdict(result)
    # log = yaml.dump(result, indent=2)
    # print(log)
    # print(result)

    result = None
    inputs = dict(args=str(args), kwargs=str(kwargs))
    function_name = f'{function.__module__}.{function.__name__}'
    log = dict(inputs=inputs, function=function_name)
    start = time.time()
    try:
      result = function(*args, **kwargs)
    except Exception as e:
      log['error'] = error=str(e)
    # finally:
    end = time.time() - start
    runtime = f'{end * 1000} ms'
    log['runtime'] = runtime
    log['result'] = result
    log = yaml.dump(log, indent=2)
    print(log)
    return result
  return wrapper


def example():
  @main
  def add(a, b):
    return a + b

  
  print(add(1, 1))
  print(add(1, []))


if __name__ == '__main__':
  example()


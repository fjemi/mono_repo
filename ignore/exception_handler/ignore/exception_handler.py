# Standard
import dataclasses as dc
import datetime as dt
from typing import Any
# Internal
# from shared.logger.logger import create_log, format_log


@dc.dataclass
class Data:
  pass


def exception_handler(func):
  # Create a log
  # log = create_log({'function_name': func.__name__})

  def wrapper(*args, **kwargs):
    # Access variable outside function scope
    nonlocal log

    result = None
    try:
      result = func(*args, **kwargs)
    except Exception as e:
      log.logging_level = 'ERROR'
      log.exception = e
      unpack_arguements(*args, **kwargs)
    log.function_inputs = {'args': args, 'kwargs': kwargs}
    return result

  wrapper()
  # print(log)
  return wrapper


def unpack_arguements(*args: Any, **kwargs: Any) -> dict:
  for arg in args:
    pass
    #print('arg', arg)
  for kwarg in kwargs.items():
    pass
    #print('kwarg', kwarg)


if __name__ == '__main__':
  import dataclasses as dc
  from typing import Any


  @dc.dataclass
  class Data:
    a: Any
    b: Any


  # @exception_handler
  def add(data: Data):
    return data.a + data.b

  result = [add(Data(1, 0)), add(Data(1, '+'))]
  print(result)

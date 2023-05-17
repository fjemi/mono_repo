# Standard
from dataclasses import dataclass, field, asdict
import time    
from typing import Any
from pprint import pprint
# import logging

from functions.exception_handler.unpack_arguements import unpack_arguments
from functions.exception_handler.format_exception import format_exception

# LOGGER = logging.getLogger() #.setLevel(logging.INFO)


@dataclass(slots=True)
class Data:
  function: str = None
  start_time: int = field(default_factory=lambda: int(time.time()))
  end_time: int = None
  arguments: Any = None
  keyword_arguments: Any = None
  exception: str = None


def exception_handler(func):
  def wrapper(*args, **kwargs):
    # Access variable outside function scope
    log = Data(function=func.__name__)
    result = None
    
    try:
      result = func(*args, **kwargs)
    except Exception as e:
      log.exception = format_exception(exception=e)
      args_kwargs = unpack_arguments(*args, **kwargs)
      log.keyword_arguments = args_kwargs.keyword_arguments
      log.arguments = args_kwargs.arguments

    log.end_time = int(time.time())
    # if log.exception:
    #   pprint(log)
      # LOGGER.log(level=0, msg=asdict(log))
    print('\n')
    pprint(result)
    pprint(log)
    return result
  return wrapper

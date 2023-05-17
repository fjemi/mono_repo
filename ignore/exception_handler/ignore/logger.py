# Standard
import datetime as dt
from time import time
import logging
import dataclasses as dc
from typing import Union, Any
import traceback
from os import getenv


@dc.dataclass
class Data:
  function_name: str = None
  function_inputs: Any = None
  start_time: int = None
  end_time: int = None
  execution_time: int = None
  logging_level: str = getenv('LOGGING_LEVEL') or 'INFO'
  exception: Exception = None


def create_log(data: Union[Data, dict]) -> Data:
  if isinstance(data, dict):
    data = Data(**data)
  # Set start time
  data.start_time = int(time())
  return data


def format_log_exception(data: Union[Data, dict]) -> Data:
  if data.exception is None:
    return Data
  
  return {
    'type': type(data.exception).__name__,
    'message': str(data.exception),
    'trace_back': traceback.format_exception(data.exception)
  }


def format_log(data: Union[Data, dict]) -> Data:
  if isinstance(data, dict):
    data = Data(**data)

  # if log.exception is not None:
  #   data.logging_level = 'ERROR'

  # Set end and execution time
  data.end_time = int(time())
  data.execution_time = data.end_time - data.start_time
  
  # Format exception

  return data


def log_log(data: Union[Data, dict]) -> Data:
  if isinstance(data, dict):
    data = Data(**data)
  # Set Function start time
  data.start_time = dt.datetime.utcnow().strftime(data.timestamp_format)
  return data


# log = create_log(Data())
print(log)

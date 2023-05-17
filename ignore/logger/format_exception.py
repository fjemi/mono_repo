from dataclasses import dataclass
from typing import Union, Optional, List
import traceback


@dataclass
class Data:
  exception: Exception
  

def format_exception(data: Union[Data, dict]) -> Optional[Data]:
  '''
  Summary
  Data
    - exception: A python exception object
  Return
    Data
  '''

  if data.exception is None:
    return data

  formatted_exception = dict(
    type=type(data.exception).__name__,
    message=str(data.exception),
    trace_back=traceback.format_exception(data.exception), )
  data.exception = formatted_exception
  return data


if __name__ == '__main__':
  data = None
  try:
    b + False
  except Exception as exception:
    print(exception)
    data = Data(exception=exception)
    data = format_exception(data)
    print(data)
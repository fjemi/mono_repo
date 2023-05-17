from dataclasses import dataclass
from typing import List
import traceback


@dataclass
class Data:
  name: str = None
  message: str = None
  traceback: List[str] = None


def format_exception(exception: Exception) -> dict:
  '''Extract and format type, message, and tracebrack from an exception'''
  # Get and format exception's traceback
  traceback_str = ''.join(traceback.format_tb(exception.__traceback__))
  traceback_str = traceback_str.replace('  ', '').replace('\n\n', '')
  traceback_list = traceback_str.split('\n')
  # Return formatted data
  data = Data(
    name=type(exception).__name__,
    message=str(exception), 
    traceback=traceback_list, )
  return data

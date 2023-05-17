# Standard
from typing import Union
from dataclasses import dataclass
from os.path import expandvars
# Internal
from functions.exception_handler.exception_handler import exception_handler


@dataclass
class Data:
    '''Store text to set enviroment variables in'''
    text: str = None


@exception_handler
def set_env_vars_in_text(data: Union[Data, str]) -> Data:
  ''''''
  if isinstance(data, str):
    data = Data(**data)

  # Map text to defined variables
  mapper = Box(WORKING_DIR=dirname(data.path))
  for key in mapper:
    data.text = data.text.replace(key, mapper[key])
  # Set environment variables
  data.text = expandvars(data.text)
  return data

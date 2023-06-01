#!/usr/bin/env python3

# from __future__ import annotations
import logging
import dataclasses as dc
import json
import yaml

from shared.get_environment import app as get_environment


THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)


@dc.dataclass
class Data:
  log_name: str
  log_path: str
  log_format: str
  module_path: str


filename = f'{ENV.WORKDIR}/logs/log'
logging.basicConfig(
  filename=filename,
  filemode='a',
  datefmt='%H:%M:%S',
  level=logging.DEBUG,
)

logger = logging.getLogger()


LEVEL_MAPPER = {
  'INFO': logger.info,
  'DEBUG': logger.debug,
  'ERROR': logger.error,
} 


def main(
  data: str, 
  level: str, 
  module_path: str | None = None,
):
  _logger = LEVEL_MAPPER[level]
  _logger(data)
  # print(dir(_logger))
  # for item in _logger.handlers:
  #   print(vars(item))
  #   print(item.baseFilename)
  # print(_logger.name)
  return


def example() -> None:
  message = 'message'
  main(message)
  
  
if __name__ == '__main__':
  example()
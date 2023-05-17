#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict

from shared.setup_data import app as setup_data
from shared.format_output import app as format_output
from shared.error_handler import app as error_handler
from shared.get_environment import app as get_environment


ENV = get_environment.main(f'module_path: {__file__}')
REMOVE_FIELDS = [
  'remove_fields',
]


@dataclass
class Data:

  remove_fields: List[str] = field(default_factory=lambda: REMOVE_FIELDS)


@error_handler.main()
def main(data: Data | dict | str) -> Data:
  data = setup_data.main(data=data, data_class=Data)
  
  
  data = format_output.main(data=data)
  return data


def example() -> None:
  data = [
    '''
    ''',
  ]
  for d in data:
    d = main(data=d)
    print(d)


if __name__ == '__main__':
  example()

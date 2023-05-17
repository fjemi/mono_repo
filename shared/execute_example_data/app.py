#!/usr/bin/env python3

import yaml
from typing import List, Callable, Any
from dataclasses import asdict

from shared.error_handler import app as error_handler


def format_data_as_yaml(data: Any, i: int = 0) -> str:
  if hasattr(data, '__dataclass_fields__'):
      data = asdict(data)
  data = {f'example {i}': data}
  data = yaml.dump(
    data, 
    indent=2,
    default_flow_style=None,
  )
  return data


def main(
  examples: List[str], 
  main_function: Callable,
) -> bool:  
  if isinstance(examples, list) is False:
    examples = yaml.safe_load(examples)['examples']
  for i, data in enumerate(examples):
    data = main_function(data=data)
    data = format_data_as_yaml(data=data, i=i)
    print('\n', data)
  return True

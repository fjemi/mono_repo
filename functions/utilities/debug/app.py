#!/usr/bin/env python3

import yaml
from dataclasses import asdict


async def main(
  request: 'fastapi.Request',
  *args,
  **kwargs,
) -> None:
  data = asdict(request.data)
  data['args'] = list(args)
  data['kwargs'] = kwargs
  try:
    data = yaml.dump(data, indent=2)
  except:
    pass
  print(data)

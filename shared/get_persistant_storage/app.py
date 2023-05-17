#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path
import shelve
from shelve import DbfilenameShelf

from api import models
from shared.get_environment import app as get_environment
from shared.setup_data import app as setup_data


THIS_MODULE_PATH = __file__


@dataclass
class Data:
  env: models.Env | None = None
  storage_name: str = 'persistant_storage.shelve'
  storage: DbfilenameShelf | None = None


def setup_persistant_storage(data: Data) -> DbfilenameShelf:
  path = Path(
    data.env.WORKDIR,
    data.env.DATA_PATH,
    data.storage_name,
  )
  storage = shelve.open(path)
  return storage


async def main(data: Data | dict | str | None = None) -> Data: 
  data = setup_data.main(data=data, data_class=Data)
  environment_data = f'module_path: {THIS_MODULE_PATH}'
  data.env = get_environment.main(data=environment_data)
  data.storage = setup_persistant_storage(data=data)
  return data


async def example() -> None:
  # Create it
  data = main()
  print(data)
  # Close it
  data.storage.close()
  print(data)


if __name__ == '__main__':
  import asyncio
  
  
  asyncio.run(example())

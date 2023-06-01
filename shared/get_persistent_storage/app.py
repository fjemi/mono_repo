#!/usr/bin/env python3

import dataclasses as dc
from pathlib import Path
import shelve
from fastapi import Request

from shared.get_environment import app as get_environment
from shared.format_main_arguments import app as format_main_arguments


THIS_MODULE_PATH = __file__
ENV = get_environment.main(module_path=THIS_MODULE_PATH)


@dc.dataclass
class Body:
  working_directory: str = ENV.WORKDIR
  data_path: str = ENV.DATA_PATH
  storage_name: str = 'persistent_storage.shelve'


@dc.dataclass
class Data:
  body: Body | None = None
  call_method: str | None = None
  storage: shelve.DbfilenameShelf | None = None


def setup_persistent_storage(data: Data) -> shelve.DbfilenameShelf:
  path = Path(
    data.body.working_directory,
    data.body.data_path,
    data.body.storage_name,
  )
  storage = shelve.open(path)
  return storage


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  working_directory: str | None = None,
  data_path: str | None = None,
  storage_name: str | None = None,
) -> shelve.DbfilenameShelf:
  data = format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  data.storage = setup_persistent_storage(data=data)
  return data


async def example() -> None:
  # Create it
  data = await main(
    working_directory=ENV.WORKDIR,
    data_path=ENV.DATA_PATH,
    storage_name='example_persistent_storage.shelve'
  )
  print(data)
  # Close it
  data.storage.close()
  print(data)


if __name__ == '__main__':
  import asyncio


  asyncio.run(example())

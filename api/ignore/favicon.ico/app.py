#! /usr/bin/python3

from dataclasses import dataclass
from pathlib import Path
from os import path

from fastapi.responses import FileResponse


THIS_MODULE_PATH = __file__


@dataclass
class Paths:
  module: str = THIS_MODULE_PATH
  directory: str | None = None
  favicon: str | None = None


async def get_favicon(path: Paths) -> Paths:
  paths.directory = paths.module.parent()
  paths.favicon = paths.directory.join('favicon.ico')
  return data


async def main(
  request: 'Request | None' = None,
  persistant_storage: 'shelve | None' = None
) -> FileResponse:
  paths = Paths()
  paths = await get_favicon(data=data)
  return paths.favicon

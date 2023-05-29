#!/usr/bin/env python3

from dataclasses import dataclass, fields
from pathlib import Path
from fastapi.responses import FileResponse

from shared.get_environment import app as get_environment


THIS_MODULE_PATH = __file__
ENV = get_environment.main({'module_path': THIS_MODULE_PATH})


@dataclass
class Data:
  filename: str = 'favicon.ico'
  directory: str = 'api.static'
  working_directory: str = ENV.WORKDIR
  response: FileResponse | None = None


@dataclass
class DataClass:
  ...


async def process_kwargs(
  data: Data,
  kwargs: dict,
) -> DataClass:
  for field in fields(data):
    if field.name not in kwargs:
      continue
    setattr(data, field.name, kwargs[field.name])
  return data


async def get_favicon(data: Data) -> FileResponse:
  # Set favicon path
  path = Path(data.working_directory)
  directories = data.directory.split('.')
  path = path.joinpath(*directories, data.filename)
  # Set response
  content_disposition = f'attachment; filename={data.filename}'
  headers = {'Content-Disposition': content_disposition}
  response = FileResponse(path=path, headers=headers)
  return response


async def main(*args, **kwargs) -> FileResponse:
  _ = args
  data = Data
  data = await process_kwargs(data=data, kwargs=kwargs)
  data.response = await get_favicon(data=data)
  return data.response

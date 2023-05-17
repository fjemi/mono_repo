#!/usr/bin/env python3

from typing import Any, ByteString
from dataclasses import dataclass
import json
from copy import deepcopy
from requests_toolbelt.multipart.decoder import MultipartDecoder


FIELD_NAME_MAPPER = {
  'filename': 'file_name',
  'content-type': 'content_type'
}


@dataclass
class JSON:
  file_name: str | None = None
  chunks_n: int = 1
  chunk_i: int = 1
  location: str = 'file_system'
  read_as: str = 'text'


@dataclass
class Binary:
  content_type: str | None = None
  content: str | None = None


@dataclass
class Data:
  _json: JSON | None = None
  binary: Binary | None = None


MAPPER = {
  'Content-Disposition': 'name',
  'Content-Type': 'content_type',
}


async def process_headers_content_type(
  key: str,
  value: str,
  store: dict,
) -> dict:
  store[key] = value.strip()
  return store


async def process_headers_content_disposition(
  key: str,
  value: str,
  store: dict,
) -> dict:
  values = value.split(';')
  for value in values:
    if value.find('=') == -1:
      continue
    value = value.split('=')
    key = value[0].strip()
    store[key] = value[1].replace('"', '').strip()
  return store
  

FORMAT_HEADERS = {
  'content-type': process_headers_content_type,
  'content-disposition': process_headers_content_disposition,
}
  

async def format_headers(
  headers: 'CaseInsensitiveDict',
) -> dict:
  store = {}
  for key, value in headers.items():
    key = key.decode('utf-8').lower()
    value = value.decode('utf-8').lower()
    function = FORMAT_HEADERS[key]
    store = await function(key=key, value=value, store=store)
  return store


async def process_content_json_data(
  content: str | bytes, 
  store: dict,
) -> dict:
  content = json.loads(content)
  store.update(content)
  return store


async def process_content_binary_data(
  content: str | bytes,
  store: dict,
) -> dict:
  store['content_type'] = deepcopy(store['content-type'])
  store['content'] = content
  del store['filename']
  del store['content-type']
  return store


FORMAT_CONTENT = {
  'json_data': process_content_json_data,
  'binary_data': process_content_binary_data,
}


async def format_content(
  content: 'CaseInsensitiveDict',
  store: dict,
) -> dict:
  function = FORMAT_CONTENT[store['name']]
  store = await function(
    content=content,
    store=store,
  )
  return store


# Map data to the correct dataclass
DATACLASS = {
  'json_data': JSON,
  'binary_data': Binary,
}


DATACLASS_FIELD = {
  'json_data': '_json',
  'binary_data': 'binary',
}


async def decode_request_form_data(
  request: 'Request',
) -> MultipartDecoder:
  form_data = MultipartDecoder.from_response(request)
  return form_data


async def parse_form_data(
  form_data: MultipartDecoder,
) -> Any:
  data = Data()
  for part in form_data.parts:
    store = {}
    # Format the headers and content
    store = await format_headers(headers=part.headers)
    store = await format_content(
      content=part.content,
      store=store,
    )
    # Create dataclass object
    name = store['name']
    data_class = DATACLASS[name]
    data_class_field = DATACLASS_FIELD[name]
    del store['name']
    data_class = data_class(**store)
    setattr(data, data_class_field, data_class)
  return data


async def format_request(request: 'Request') -> 'Request':
  body = request.data.data['form']
  # Multipart decoder requires this attribute to be set
  setattr(request, 'content', body)
  return request


async def main(request: 'Request') -> Any:
  request = await format_request(request=request)
  form_data = await decode_request_form_data(
    request=request)
  form_data = await parse_form_data(
    form_data=form_data)
  return form_data

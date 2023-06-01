#! /usr/bin/python3

from typing import List, Dict
import dataclasses as dc
import yaml
# from requests_toolbelt.multipart.decoder import MultipartDecoder

from fastapi import Request, HTTPException


@dc.dataclass
class DataClass:
  # Type hint for generic dataclass
  pass


ATTRIBUTE_TYPES = {
  'str': lambda attributes: [attributes],
  'list': lambda attributes: attributes,
  'nonetype': lambda attributes: [],
}


async def pre_process_attributes(
  attributes: List[str] | str | None,
) -> List[str]:
  attributes_type = type(attributes).__name__.lower()
  if attributes_type not in ATTRIBUTE_TYPES:
    raise HTTPException(
      status_code=400,
      detail='Bad Request',
    )
  switcher = ATTRIBUTE_TYPES[attributes_type]
  attributes = switcher(attributes=attributes)
  return attributes


async def get_headers(request: Request) -> 'Headers':
  store = {}
  for key, value in request.headers.items():
    key = key.lower().replace('-', '_')
    store[key] = value
  return store


async def case_json_and_body_are_null(attribute: dict) -> dict:
  _ = attribute
  return {}


BODY_TYPE_SWITCHER = {

}


async def case_body_is_not_null(attribute: dict) -> dict:
  body = attribute['body']

  try:
    return yaml.safe_load(body)
  except Exception:
    # Form data
    return {}


async def case_json_is_not_null(attribute: dict) -> dict:
  return attribute['json']


GET_BODY = {
  '.': case_json_and_body_are_null,
  'body.':case_body_is_not_null,
  '.json': case_json_is_not_null,
  'body.json': case_json_is_not_null,
}


async def get_body(request: Request) -> 'Body':
  attribute = {'body': None, 'json': None}
  for name, value in attribute.items():
    if hasattr(request, name):
      try:
        value = await getattr(request, name)()
        from copy import deepcopy
        value = deepcopy(value)
      except Exception:
        pass
    attribute[name] = value

  cases = [
    'body' if attribute['body'] is not None else '',
    'json' if attribute['json'] is not None else '',
  ]
  cases = '.'.join(cases)
  switcher = GET_BODY[cases]
  body = await switcher(attribute=attribute)
  return body


async def get_path_params(request: Request) -> dict:
  return request.path_params


# pylint: disable=protected-access
async def get_query_params(request: Request) -> dict:
  if not hasattr(request.query_params, '_dict'):
    return {}
  return request.query_params._dict


async def get_method(request: Request) -> str:
  return {'value': request.method}


async def get_form(request: Request) -> bytes | str:
  form = await request.form()
  if len(form) == 0:
    return {}

  form = form._dict
  return form


GET_REQUEST_ATTRIBUTE = {
  'headers': get_headers,
  'body': get_body,
  'path_params': get_path_params,
  'query_params': get_query_params,
  'method': get_method,
  'form': get_form,
}


async def get_request_attributes(
  request: Request,
  attributes: List[str],
) -> Dict:
  store = {}
  for attribute in attributes:
    function = GET_REQUEST_ATTRIBUTE[attribute]
    attribute_object = await function(request=request)
    store[attribute] = attribute_object
  return store


DEFAULT_FIELDS = ['str', 'int', 'float', 'nonetype']


async def get_attribute_data_classes(
  attributes: Dict[str, DataClass],
  data_classes: Dict[str, DataClass],
) -> Dict[str, DataClass]:
  store = {}

  for name, data_class in data_classes.items():
    data_class = data_class()
    attribute = attributes[name]

    if attribute is None:
      continue

    for field in dc.fields(data_class):
      if field.name not in attribute:
        continue
      attribute_value = attribute[field.name]
      if attribute_value is None:
        continue
      setattr(data_class, field.name, attribute_value)

    store[name] = data_class
  return store


async def create_consolidated_dataclass(
  attributes: Dict[str, DataClass],
  main_data_class: DataClass,
) -> DataClass:
  if main_data_class:
    return main_data_class()

  keys = list(attributes.keys())
  fields = []
  for key in keys:
    hint = f'{key} | None'
    field = [
      key.lower(),
      hint,
      None,
    ]
    fields.append(field)
  data = dc.make_dataclass(cls_name='Data', fields=fields)
  return data()


async def add_attributes_to_consolidated_dataclass(
  attributes: Dict[str, DataClass],
  main_data_class: DataClass,
) -> DataClass:
  data = main_data_class
  for key, value in attributes.items():
    key = key.lower()
    setattr(data, key, value)
  return data


async def main(
  request: Request,
  data_classes: Dict[str, DataClass] | None = None,
  main_data_class: DataClass | None = None,
) -> 'Data':
  attributes = await get_request_attributes(
    request=request,
    attributes=list(data_classes.keys()),
  )
  attributes = await get_attribute_data_classes(
    attributes=attributes,
    data_classes=data_classes
  )
  main_data_class = await create_consolidated_dataclass(
    attributes=attributes,
    main_data_class=main_data_class,
  )
  main_data_class = await add_attributes_to_consolidated_dataclass(
    attributes=attributes,
    main_data_class=main_data_class,
  )
  return main_data_class

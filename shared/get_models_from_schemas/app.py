import dataclasses as dc
from typing import Dict, Any, List
from os import path
from copy import deepcopy
import yaml


@dc.dataclass
class Model:
  ...


@dc.dataclass
class Models:
  names: List[str] | None = None
  models: List[Model] | None = None


def get_schemas(
  yml_path: str = None,
  py_path: str = None,
) -> Dict:
  if py_path:
    root = path.dirname(py_path)
    yml_path = path.join(root, 'schemas.yml')
  schemas = None
  with open(
    file=yml_path,
    mode='r',
    encoding='utf-8',
  ) as file:
    yml_data = yaml.safe_load(file)
    schemas = yml_data['schemas']
  return schemas


def set_fields(schema: Dict) -> List[Any]:
  model_fields = []
  field_values = {
    'name': None, 
    'type': None, 
    'default': None,
  }

  for field in schema['fields']:
    values = deepcopy(field_values)
    for name in values:
      if name not in field.keys():
        continue
      value = field[name]
      values[name] = value
    values = list(values.values())
    model_fields.append(values)
  return model_fields


def get_models_as_dict(schemas: Dict) -> Dict[str, Model]:
  models = {}
  for name, schema in schemas.items():
    fields = set_fields(schema=schema)
    model = dc.make_dataclass(
      name,
      fields=fields,
      slots=True,
      kw_only=True,
    )
    models[name] = model
  return models


def get_models_as_dataclass(schemas: Dict) -> Models:
  models = Models(names=[], models=[])
  for name, schema in schemas.items():
    fields = set_fields(schema=schema)
    model = dc.make_dataclass(
      name,
      fields=fields,
      slots=True,
      kw_only=True,
    )
    models.names.append(name)
    models.models.append(model)
  return models


MAIN = {
  'dict': get_models_as_dict,
  'dataclass': get_models_as_dataclass,
}


def main(
  yml_path: str = None,
  py_path: str = None,
  return_type: str = 'dict',
) -> Dict[str, Model] | Models:
  schemas = get_schemas(
    py_path=py_path,
    yml_path=yml_path,
  )
  function = MAIN[return_type]
  models = function(schemas=schemas)
  return models


def example() -> None:
  py_path = path.dirname(__file__)
  py_path = path.join(py_path, 'test_resources/app.py')
  items = [
    main(py_path=py_path),
    main(py_path=py_path, return_type='dataclass'),
  ]
  for item in items:
    print(str(item))


if __name__ == '__main__':
  example()

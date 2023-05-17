

from dataclasses import dataclass
import yaml


class Store:
  pass


@dataclass
class Form:
  _json: Store | None = None
  binary: Store | None = None


import yaml

form_data = '''
  _json:
    file_name: file_name
    time: time
  binary:
    content: !!binary |
      dGVzdDe=
'''
form_data = yaml.safe_load(form_data)
print(form_data)

form = Form(**form_data)
print(form)
import dataclasses as dc
from typing import List, Any, Dict
from os.path import exists, splitext
from io import TextIOWrapper
import yaml
import csv


@dc.dataclass
class Data:
  path: str = None
  cast_as: str = 'dict'


def case_yml_to_dict(stream: TextIOWrapper) -> Dict[Any, Any]:
  return yaml.safe_load(stream=stream)


def case_csv_to_dict(stream: TextIOWrapper) -> List[Dict[Any, Any]]: 
  reader = csv.reader(stream)
  fields = []
  store = {}
  count = 0
  for row in reader:
    # Add each value to its key/list 
    # in its associated dictionary
    if count != 0:
      for field in fields:
        index = fields.index(field)
        store[field].append(row[index])
    # Initialize dictionary with keys as field 
    # namesvalues as empty lists
    if count == 0:
      fields = row
      for name in row:
        store[name] = []
    count += 1
  return store


def case_csv_to_list_dict(stream: TextIOWrapper) -> List[Dict[Any, Any]]: 
  reader = csv.DictReader(stream)
  store = []
  for row in reader:
    store.append(row)
  return store


GET_FILE_CONTENTS = {
  ".yml_dict": case_yml_to_dict,
  ".json_dict": case_yml_to_dict,
  ".csv_dict": case_csv_to_dict,
  ".csv_list_dict": case_csv_to_list_dict,
}


def get_file_contents(data: Data) -> Any:
  extension = splitext(data.path)[1]
  _case = f'{extension}_{data.cast_as}'
  with open(data.path, 'r', encoding="utf-8") as stream:
    function = GET_FILE_CONTENTS[_case]
    return function(stream=stream)


SETUP_DATA = {
  'str': lambda data: Data(path=data),
  'Data': lambda data: data,
  'dict': lambda data: Data(**data),
}


def setup_data(data: Data | str | Dict) -> Data:
  _case = type(data).__name__
  return SETUP_DATA[_case]


def main(data: Data | str | Dict) -> Data:
  data = setup_data(data=data)(data)
  return get_file_contents(data=data)
  

def example() -> None:
  test_resources_dir = __file__.replace('app.py', 'test_resources/')
  

  example = {
    0: main(data=test_resources_dir + 'test.csv'),
    1: main(data={'path': test_resources_dir + 'test.yml'}),
    2: main(data={'path': test_resources_dir + 'test.csv'}),
    3: main(data={'path': test_resources_dir + 'test.yml'}),
  }
  print(example, sep='\n')


def example_with_string_to_stream() -> None:
  #Convert string to stream
  string = 'field_0,field_1\nvalue_00,value_01\nvalue_10, value11'
  from io import StringIO
  stream = StringIO(string)
  stream = case_csv_to_list_dict(stream)
  print(stream, sep='\n')


if __name__ == '__main__':
  example()
  example_with_string_to_stream()


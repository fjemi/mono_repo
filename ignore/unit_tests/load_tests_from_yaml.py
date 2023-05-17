import yaml
from typing import Union, List
from shared.unit_tests.models import Tests, Case


def load_tests_from_yaml(data: Union[Tests, dict]) -> List[Case]:
  '''
  Summary
    Loads and returns test data from a yaml file
  Paramters
    filepath: Path to a python file
  Returns
    List of test data
  '''
  if isinstance(data, dict):
    data = Tests(**data)
  # Store test data
  store = []
  # Set path for yaml file
  yaml_path = data.filepath.replace('.py', '.yml')
  # Load and store test data
  with open(yaml_path, 'r') as file:
    yaml_data = yaml.safe_load(file)['tests']
    for case in yaml_data:
      store.append(Case(**case))
  return store

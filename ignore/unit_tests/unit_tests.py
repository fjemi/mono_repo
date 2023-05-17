from shared.unit_tests.models import Tests
from shared.unit_tests.load_tests_from_yaml import load_tests_from_yaml
from shared.unit_tests.execute_tests import execute_tests
from shared.unit_tests import add

from typing import Union


def unit_tests(tests: Union[Tests, dict]) -> None:
  '''
  Summary
    Loads tests from a yaml file and runs them
  Parameters
    filepath: Path to a python file to tests
    tests: List of unit tests
  Returns
    None
  '''
  if isinstance(tests, dict):
    tests = Tests(**tests)
  tests.cases = load_tests_from_yaml(tests)
  execute_tests(tests=tests)
  return


if __name__ == '__main__':
  
  filepath = __file__
  module = add
  tests = dict(filepath=filepath, module=module)
  result = unit_tests(tests=tests)
  assert result is None



import load_tests_from_yaml as module
from shared.unit_tests.unit_tests import unit_tests


def load_tests_from_yaml_test() -> None:
  ''''''
  filepath = __file__
  tests = dict(filepath=filepath, module=module)
  unit_tests(tests=tests)

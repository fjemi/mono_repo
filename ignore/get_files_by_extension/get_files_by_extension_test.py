import get_files_by_extension as module
from shared.unit_tests.unit_tests import unit_tests

def get_files_by_extension_test() -> None:
  ''''''
  # Setup
  filepath = __file__
  tests = dict(filepath=filepath, module=module)
  unit_tests.unit_tests(tests=tests)
  # Test that these helper functions are called



# f = lambda:  get_files_by_extension_test()
# f()
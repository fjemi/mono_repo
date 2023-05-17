# TODO: Testing framework

# Set module to test
import app

def collect_tests() -> None:
  '''Run tests defined within a YAML file'''
  filepath = __file__
  tests = dict(filepath=filepath, module=module)
  unit_tests(tests=tests)

# Using lambda run tests. Setup allows all test 
# files to be the same (unique unit test names are not needed)
execute_test = lambda: collect_tests()
execute_test
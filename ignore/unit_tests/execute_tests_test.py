from shared.unit_tests import execute_tests, add as module
from shared.unit_tests.models import Tests, Case
import pytest


def execute_tests_test() -> None:
  ''''''
  # Setup
  cases = [
    Case(
      function='add',
      description='''Format a test should be. This test should fail.''',
      inputs={'a': 1, 'b': 1},
      output=3, 
      output_type='int'), ]
  tests = Tests(cases=cases, module=module)
  # Should raise an exception when the test fails
  with pytest.raises(AssertionError) as e:
    execute_tests.execute_tests(tests=tests)
  
  cases = [
  Case(
    function='add',
    description='''Format a test should be. This test should pass.''',
    inputs={'a': 1, 'b': 1},
    output=2,
    output_type='int', ),  ]
  tests = Tests(cases=cases, module=module)
  # Test should pass and not raise an exception
  execute_tests.execute_tests(tests=tests)

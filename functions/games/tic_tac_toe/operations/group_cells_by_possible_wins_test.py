from utils.unit_tests.unit_tests import unit_tests
import group_cells_by_possible_wins


def group_cells_by_possible_wins_test() -> None:
  ''''''
  module = group_cells_by_possible_wins
  filepath = __file__
  tests = dict(filepath=filepath, module=module)
  unit_tests(tests=tests)


# from utils import get_test_data
# from typing import List


# TESTS = get_test_data.main({'filepath': __file__})


# def get_test_data_test(tests = TESTS) -> None:
#   ''''''

#   # Set function from the module to test
#   function = getattr(module, test.function)
#   # Function should produce expected output
#   # when provided inputs from the yaml file
#   output = function(test.inputs)
#   print({'function': test.function, 'test': test.description})
#   expected = module.Game(**test.output)
#   assert output == expected


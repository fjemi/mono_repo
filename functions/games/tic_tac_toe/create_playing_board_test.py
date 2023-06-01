import create_playing_board
from utils.unit_tests.unit_tests import unit_tests


def create_playing_board_test() -> None:
  ''''''
  filepath = __file__
  module = create_playing_board
  tests = dict(filepath=filepath, module=module)
  unit_tests(tests=tests)

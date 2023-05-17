from unittest.mock import create_autospec
import unittest
import get_input


# Method 1 and 2 both work
# Method 1
# add.main = create_autospec(add.main, return_value=3)
# Method 2
spec = get_input.get_input
return_value = 3
mock = create_autospec(spec=spec, return_value=return_value)
setattr(get_input, 'get_input', mock)


def test_add():
  c = get_input.main()
  assert c == 3
  get_input.get_input.assert_called_with()
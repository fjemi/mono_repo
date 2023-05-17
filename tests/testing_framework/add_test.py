from unittest.mock import create_autospec
import unittest
import add


# Method 1 and 2 both work
# Method 1
# add.main = create_autospec(add.main, return_value=3)
# Method 2
spec = add.main
return_value = 3
mock = create_autospec(spec=spec, return_value=return_value)
setattr(add, 'main', mock)


def test_add():
  data = add.Data(1, 2)
  c = add.main(data)
  assert c == 3
  add.main.assert_called_with(data)
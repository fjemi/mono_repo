from unittest.mock import create_autospec
import unittest
import get_timestamp
from datetime import datetime


mock = create_autospec(get_timestamp.main, return_value=1)
setattr(get_timestamp, 'main', mock)


def test_get_timestamp():
  result = get_timestamp.main()
  assert result == 1
  get_timestamp.main.assert_called()


# mock = create_autospec(datetime.utcnow, return_value=1)
# setattr(datetime, 'utcnow', mock)

datetime.utcnow = create_autospec(datetime.utcnow, return_value=1)

print(datetime.utcnow())
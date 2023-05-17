# Module to test
from format_exception import format_exception


def add(a, b):
  '''Function to use in tests'''
  return a + b


def format_exception_test() -> None:
  '''Test that exceptions are formatted'''
  # Should return a formatted exception
  try:
    raise TypeError('TypeError')
  except Exception as e:
    formatted_exception = format_exception(exception=e)
    assert formatted_exception.name == 'TypeError'
    assert formatted_exception.message == 'TypeError'
    assert len(formatted_exception.traceback) != 0

  # Should return a formatted exception
  try:
    raise RuntimeError
  except Exception as e:
    formatted_exception = format_exception(exception=e)
    assert formatted_exception.name == 'RuntimeError'
    assert formatted_exception.message == ''
    assert len(formatted_exception.traceback) != 0

  # Should return a formatted exception
  try:
    add(1, None)
  except Exception as e:
    formatted_exception = format_exception(exception=e)
    assert formatted_exception.name == 'TypeError'
    assert formatted_exception.message == "unsupported operand type(s) for +: 'int' and 'NoneType'"
    assert len(formatted_exception.traceback) != 0
    
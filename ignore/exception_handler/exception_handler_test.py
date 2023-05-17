from functions.exception_handler.exception_handler import exception_handler


@exception_handler
def add(a, b):
  '''Decorating this function with the exception handler for testing'''
  return a + b


def exception_handler_test() -> None:
  '''Test the exception handler'''
  # Should return the expected result of the function when no error occurs
  c = add(a=1, b=1)
  assert c == 2

  # Should catch error and return None when error 
  # occurs within the decorated function. 
  c = add(a=1, b=None)
  assert c == None

  # Should catch error and return None when error 
  # occurs within the decorated function. 
  c = add()
  assert c == None


if __name__ == '__main__':
  dataset = [Data(a=1, b=1), Data(a=1, b=None)]
  for data in dataset:
    result = add(data)
    print(result)
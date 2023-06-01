from threading import Thread, Lock
from typing import Callable, List, Dict, Any
# from types import ModuleType
import dataclasses as dc
import dacite
import time
import inspect

STORE = []
# THREADS = []
LOCK = Lock()

@dc.dataclass
class Data:
  # module: ModuleType | None = None
  target: Callable | None = None
  args: List[List[Any]] | List[Any] | None = None
  kwargs: List[Dict] | Dict | None = None
  threads: List[Thread] | None = None
  store_name: str = 'STORE'
  

def case_main_args_data_data(main_args: Dict) -> Data:
  '''Case where the data main arg is a dataclass'''
  return main_args['data']


def case_main_args_data_dict(main_args: Dict) -> Data:
  '''Case where the data main arg is a dataclass`'''
  return dacite.from_dict(Data, main_args['data'])


def case_main_args_data_none(main_args: Dict) -> Data:
  '''Case where individuals args are passed in'''
  return Data(
    target=main_args['target'],
    kwargs=main_args['kwargs'],
    args=main_args['args'],
    threads=main_args['threads'],
  )


SETUP_DATA = {
  0: case_main_args_data_data,
  1: case_main_args_data_dict,
  2: case_main_args_data_none,
}


def setup_data(main_args: dict) -> Data:
  '''Returns a `Data` object from the args passed into the main function'''
  conditions = [
    hasattr(main_args['data'], '__dataclassfields__'),
    isinstance(main_args['data'], dict) is True,
    main_args['data'] is None,
  ]
  _case = conditions.index(1)
  function = SETUP_DATA[_case]
  return function(main_args=main_args)


CONVERT_DATA_FIELDS_TO_LISTS = {
  'NoneType': lambda value: [],
  'list': lambda value: value,
  '*': lambda value: [value]
}


def convert_datafields_to_lists(data: Data) -> Data:
  '''Converts field values that are not lists to lists'''
  excludefields = ['target', 'store_name']
  
  for field in dc.fields(data):
    if field.name in excludefields:
      continue
    value = getattr(data, field.name)
    _type = type(value).__name__
    # Handle `Any` types
    if _type not in ['NoneType', 'list']:
      _type = '*'
    function = CONVERT_DATA_FIELDS_TO_LISTS[_type]
    value = function(value=value)
    setattr(data, field.name, value)
  return data


def create_threads(data: Data) -> List[Thread]:
  '''Returns a list of threads created for a target function and each of its 
  individual args and kwargs.'''
  store = []
  
  # Threads with args passed into function
  n = len(data.args)
  for i in range(n):
    store.append(Thread(
      target=data.target,
      args=data.args[i],
    ))
    # Lock to prevent duplicate threads from being created
    with LOCK:
      time.sleep(0.1)

  # Threads with kwargs passed into function
  n = len(data.kwargs)
  for i in range(n):
    store.append(Thread(
      target=data.target,
      kwargs=data.kwargs[i],
    ))
    # Lock to prevent duplicate threads from being created
    with LOCK:
      time.sleep(0.1)
  
  return store


def start_threads(threads: List[Thread]) -> bool:
  '''Runs threads in parallel and waits for each thread to finish before 
  returning True'''
  # Run threads in parallel
  for thread in threads:
    thread.start()

  # Wait for each thread to terminate
  for thread in threads:
    thread.join()

  return True


def get_store_from_targets_module(
  target: Callable, 
  store_name: str,
) -> List[Any]:
  '''Returns a global variable, from the target function's module, that's used 
  to store results from executing the target in multiple threads.'''
  module = inspect.getmodule(target)
  if hasattr(module, store_name) is True:
    return getattr(module, 'STORE')
  return []
  

def main(
  data: Data | dict = None, 
  target: List[Callable] | Callable = None, 
  kwargs: List[dict] | dict = None,
  args: List[Any] = None,
  threads: List[Thread] = None,
  store_name: str = None,
) -> List[Any]:
  '''An orchestration function that's used to execute the other functions within
  this module'''
  # Setup
  data = setup_data(main_args=locals())
  data = convert_datafields_to_lists(data=data)
  data.threads = create_threads(data=data)
  start_threads(threads=data.threads)
  return get_store_from_targets_module(
    target=data.target, 
    store_name=data.store_name,
  )


def example() -> None:
  from test_resources import app as test_resources


  data = main(
    target=test_resources.hello_world,
    args=[[None], ['Earth']],
    kwargs=[dict(name='Mars'), dict(name=None), dict(name='Venus')],
    threads=None,
  )
  print(data)


if __name__ == '__main__':
  example()

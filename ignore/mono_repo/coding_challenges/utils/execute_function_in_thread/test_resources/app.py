from time import time, ctime
import threading
from dataclasses import dataclass, field, asdict
import yaml


# Global variable to store results from 
# executing target functions in threads
STORE = []


@dataclass 
class Time:
  start: str | float | None = None
  end: str | float | None = None
  run: str | float | None = None


@dataclass
class Data:
  _time: Time = field(default_factory=lambda: Time())
  thread_name: str | None = None


HELLO_WORLD = {
  'str': lambda name: f'Hello {name}',
  'NoneType': lambda name: 'Hello World'
}


def format_time(data: Data) -> str:
  '''Calculates process run time, formats time objects, and returns the 
  dataclass as a YAML string'''
  data._time.run = f'{(data._time.end - data._time.start) * 1000} ms'
  data._time.start = ctime(data._time.start)
  data._time.end = ctime(data._time.end)
  data = asdict(data)
  data = yaml.dump(data, indent=2)
  return data


def hello_world(name: str = None) -> str:
  '''Returns the greeting hello world. Use as an example for setting up 
  functions as targets to be threaded'''
  data = Data(_time=Time(start=time()))
  data.thread_name = threading.current_thread().name

  _type = type(name).__name__
  function = HELLO_WORLD[_type]
  result = function(name=name)
  global STORE
  STORE.append(result)

  data._time.end = time()
  data = format_time(data=data)
  print(data)
  return


if __name__ == '__main__':
  hello_world()
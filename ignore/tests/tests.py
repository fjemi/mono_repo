#!/usr/bin/env python3

from os.path import dirname, abspath
from os import chdir
import pytest
from typing import List

# set tests directory
TESTS_DIR = dirname(abspath(__file__)) + '/'

def execute_pytests(paths: List[str]) -> None:
  ''' Allows running pytests in subdirectories
  :params paths: subdirectories in `tests` that contain pytest files
  :type paths: List[str]
  :rtype: None
  '''
  
  for path in paths:
    # set path for current working directory
    chdir(TESTS_DIR + path)
    # execute pytests in cwd
    PT = pytest.main()
    # exit loop if a pytest fails, 
    if PT.value != 0:
      break
    
  return None
  
if __name__ == '__main__':
  # subdirectories in `tests` where pytests are located
  paths = [
    ''
  ]
  
  execute_pytests(paths)
  

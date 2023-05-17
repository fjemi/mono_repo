from dataclasses import dataclass, asdict, field
from typing import Any, List, Union, Dict
from types import ModuleType


@dataclass
class Case:
  '''
  Summary
    Store s test cases
  Attributes
    function: The function to test
    description: A Description of the test
    inputs: Inputs to tests the fucntion with
    output: The expected output of the function
    passed: Whether the tests passed
  '''
  function: str = None
  description: str = None
  inputs: dict = None
  output: dict = None
  output_type: str = 'dataclass'
  passed: Dict[str, bool] = field(default_factory=lambda: {})


@dataclass
class Tests:
  '''
  Summary
    Store data from a yaml for testing a module and its functions
  Attributes
    filepath: The path to a .py file
    module: The module to test. Set in the `*_test.py` file.
    cases: Store of test cases to run
  '''
  filepath: str = __file__
  module: ModuleType = None
  cases: List[Case] = field(default_factory=lambda: [])

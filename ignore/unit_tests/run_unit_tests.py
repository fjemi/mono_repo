from dataclasses import dataclass
from typing import List, Any, Union

from functions.type_handler.type_handler  import type_handler
from functions.exception_handler.exception_handler import exception_handler


@dataclass
class Data:
  module: str = None
  function: str = None
  dataclass: Any = None
  name: str = None
  arguements: Any = None
  expected_result: Any = None
  expected_result_type: str = None


@exception_handler
def run_unit_tests(data: Union[Data, List[Data]]) -> List:
  ''''''

  if isinstance(data, Data):
    data = [data]

  results_store = []

  for i in range(len(data)):
    print(i)

  return results_store


run_unit_tests(Data())
run_unit_tests([Data(), Data(), ])
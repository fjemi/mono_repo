# Standard
import dataclasses as dc
from typing import Union, Optional
# Internal
# from shared.main import exception_handler


@dc.dataclass
class Data:
  number: Union[int, float] = None
  operation: str = 'absolute_value'
  result: Union[float, int] = None


# @exception_handler
def absolute_value(data: Union[Data, dict]) -> Optional[Data]:
  '''
  '''
  if isinstance(data, dict):
    data = Data(**data)

  data.result = data.number - 0
  if data.result < 0:
    data.result = -1 * data.result
  return data


if __name__ == '__main__':
  data = {'number': 5}
  data = absolute_value(data)
  print(data)

  data = Data(number=-5)
  data = absolute_value(data)
  print(data)

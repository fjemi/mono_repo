#!/usr/bin/python

# Standard
import dataclasses as dc
from typing import Any, Union, List


@dc.dataclass(slots=True)
class KeywordArgument:
  '''
  Description:
    Stores the key and value for a keyword value
  Attributes:
    key: Argument's keyword
    value: Argument's value
  '''
  key: str = ''
  value: Any = None


@dc.dataclass(slots=True)
class Inputs:
  '''
  Description
    Stores non-positional arguments and positional (keyword) arguments
    for a function
  Attributes
    arguments: Non-positional arguments
    keyword_arguments: Positional arguments
  '''
  arguments: List[Any] = dc.field(default_factory=lambda: [])
  keyword_arguments: List[KeywordArgument] = dc.field(
    default_factory=lambda: [])


def unpack_arguments(*args: Any, **kwargs: Any) -> Inputs:
  '''
  Description
    Unpacks arguements and keywords arguments
  Parameters
    *args: Arbitrary arguments
    **kwargs: Arbitrary keyword arguments
  Returns
    Unpacked arguments and keyword arguments in a dataclass
  '''
  inputs = Inputs()
  # Extract non-keyword and keyword arguments
  for arg in args:
    inputs.arguments.append(arg)
  for key, value in kwargs.items():
    inputs.keyword_arguments.append(KeywordArgument(key=key, value=value))
  return inputs


def main() -> None:
  '''Example usage'''
  import pprint as pp

  args = ('arg1', 'arg2', 'arg3')
  kwargs = {'arg1' : 'arg1', 'arg2' : 'arg2', 'arg3' : 'arg3'}

  inputs = unpack_arguments(*args, **kwargs)
  pp.pprint(object=dc.asdict(inputs), indent=2, width=80, compact=False)


if __name__ == '__main__':
  main()

  # inputs = unpack_arguments(*args, **kwargs)
  # assert len(inputs.arguments) == len(args)
  # assert len(inputs.keyword_arguments) == len(kwargs)
  # for keyword_arguement in inputs.keyword_arguments:
  #   assert kwargs[keyword_arguement.keyword] == keyword_arguement.argument
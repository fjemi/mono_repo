#!/usr/bin/env python3

# TODO: fix output. make stateless and work with an api

from copy import deepcopy
from random import randint
from typing import List
from dataclasses import dataclass, field
import sys

from api import models as api_models
from functions.security.authentication import app as authentication


@dataclass
class Headers(api_models.Headers):
  bearer: str | None = None


@dataclass
class Body(api_models.Body):
  user_id: str = 'user_00'
  guess: int | None = None
  upper_bound: int = 100
  lower_bound: int = 0


@dataclass
class State:
  upper_bound: int | None = None
  lower_bound: int | None = None
  guess: int | None = None


@dataclass
class Data:
  body: Body | None = None
  states: List[State] | None = None
  number: int | None = None
  guessed_correctly: bool = False


@dataclass
class Bounds:
  upper: int = 100
  lower: int = 0


@dataclass
class Data:
  body: Body | None = None
  bounds: List[Bounds] = field(default_factory=lambda: [])
  guesses: List[int] = field(default_factory=lambda: [])
  messages: List[str] = field(default_factory=lambda: [])
  correct_guess: bool = False


def get_lower_and_upper_bounds(
  lower_bound: int,
  upper_bound: int,
  guess: int,
  number: int,
) -> Bounds:

  # Conditions and cases for a guess, number, and lower/upper bound
  conditions = str([
    int(guess < lower_bound or guess > upper_bound),
    int(guess >= number),
    int(guess <= number)
  ])
  cases = {
    '[1, 0, 1]': 'exceeds_bounds',
    '[1, 1, 0]': 'exceeds_bounds',
    '[0, 1, 1]': '=number',
    '[0, 0, 1]': '<=number',
    '[0, 1, 0]': '>=number',
  }
  # Set bounds based on conditions
  switcher = {
    'exceeds_bounds': Bounds(lower=lower_bound, upper=upper_bound),
    '=number': Bounds(lower=number, upper=number),
    '<=number': Bounds(lower=guess, upper_bound=upper_bound),
    '>=number': Bounds(lower=lower_bound, upper=guess)
  }
  conditions_case = cases[conditions]
  bounds = switcher[conditions_case]
  return bounds


def get_message(
  guess: int,
  upper_bound: int,
  lower_bound: int,
) -> str:
  
  condition = int(lower_bound != upper_bound)
  switcher = {
    1: lambda: f'Guess a number between {lower_bound} and {upper_bound}: ',
    0: lambda: f'Good guess! {guess} is the correct number.'
  }
  message = switcher[condition]()
  return message


# TODO: API and store results in an S3 bucket
# dev env would store to data/user within app directory
def get_input(string: str = ''):
  return input(string)


def get_guess(
  message: str, 
  previous_guess: int, 
  correct_guess: bool,
) -> int:
  '''
  # Description
  Gets a number entered by a user from the CLI and returns
  it within a Guess object
  '''
  if correct_guess is True:

    print(message)
    sys.exit(0)
    # return None
  # Get user input via CLI
  number = get_input(string=message)
  # Handle non-numeric inputs
  if number.isdigit() is False:
    return previous_guess
  return int(number)


# def set_processed_input_result(data: Union[Data, dict]) -> str:
#   '''
#   # Description
#   Compares a user's guess to the randomly generated
#   '''

#   # User's guess is outside the bounds interval
#   if data.guess < data.lower_bound or data.guess > data.upper_bound:
#     return ''
#   # User's guess is greater/less than the number
#   if data.guess > data.number:
#     return '<'
#   if data.guess < data.number:
#     return '>'
#   # User's guess is the correct number
#   if data.guess == data.number:
#     return '='

async def process_request_args(_locals: dict) -> Data:
  request = _locals['request']



async def process_non_request_args(_locals: dict) -> Data:
  del _locals['request']
  body = Body()
  for key, value in _locals.items():
    if value is None:
      continue
    setattr(body, key, value)
  data = Data(body=body)
  return data


PROCESS_MAIN_ARGS = {
  'request': process_request_args,
  'non_request': process_non_request_args,
}


async def process_main_args(_locals: dict) -> Data:
  _case = 'request' if _locals['request'] else 'non_request'
  switcher = PROCESS_MAIN_ARGS[_case]
  data = await switcher(_locals=_locals)
  return data


async def get_response(data: Data) -> api_models.Response:
  data = None

  data = api_models.Response(data=data)
  return data


# pylint: disable=unused-argument
@authentication.decorator_factory(authenticate=False)
async def main(
  request: api_models.Request | None = None,
  user_id: str | None = None,
  guess: int | None = None,
  lower_bound: int | None = None,
  upper_bound: int | None = None,
) -> api_models.Response:
  data = await process_main_args(_locals=locals())


  data = await get_response(data=data)
  return data
  # remain_in_loop = True
  # while remain_in_loop is True:
  #   data = deepcopy(store[-1])

  #   # Condition to exit loop
  #   if data.guess == data.number and data.result == '=':
  #     remain_in_loop = False

  #   # Chain functions
  #   data = set_lower_and_upper_bounds(data=data)
  #   data.input_message = get_input_message(data=data)
  #   data.guess = get_user_input(data=data)
  #   data.result = set_processed_input_result(data=data)
  #   store.append(data)

  # return store[-1].input_message


def example() -> None:
  data = '''
    number: 2
    lower_bound: 0
    upper_bound: 10
    guess: 2
    input_message: input_message
    result: '='
  '''
  data = main(data=data)
  print(data)


if __name__ == '__main__':
  example()

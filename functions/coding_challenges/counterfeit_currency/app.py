#!usr/bin/env python3

from typing import List
from dataclasses import dataclass, field, asdict
import yaml

from api import models


VALID_DENOMINATIONS = [10, 20, 50, 100, 200, 500, 1000]
CHAR_N_BOUNDS = [10, 12]
YEAR_BOUNDS = [1900, 2019]


@dataclass
class Body(models.Body):
  serial_numbers: List[str] | None = None
  valid_denominations: List[int] = field(
    default_factory=lambda: VALID_DENOMINATIONS)
  char_n_bounds: List[int] = field(default_factory=lambda: CHAR_N_BOUNDS)
  year_bounds: List[int] = field(default_factory=lambda: YEAR_BOUNDS)


@dataclass
class RequestData(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: RequestData | None = None


@dataclass
class Currency:
  serial_numbers: List[str] | None = None
  denominations: List[int] | None = None
  total: int = 0


@dataclass
class Data:
  body: Body | None = None
  currency: Currency | None = None


async def validate_uppercase_alpha_chars(serial_number: str) -> int:
  chars = serial_number[:3] + serial_number[-1:]
  cases = [
    chars.upper() != chars,
    chars.isalpha() is False,
  ]
  cases = sum(cases)
  return cases


async def validate_length(
  serial_number: str,
  bounds: List[int],
) -> int:
  n = len(serial_number)
  cases = [
    n < bounds[0],
    n > bounds[1],
  ]
  cases = sum(cases)
  return cases


async def validate_print_year(
  serial_number: str,
  bounds: List[int],
) -> int:
  print_year = serial_number[3:7]

  try:
    print_year = int(print_year)
  except ValueError:
    print_year = -1000

  cases = [
    print_year < bounds[0],
    print_year > bounds[1],
  ]
  cases = sum(cases)
  return cases


async def validate_serial_numbers(data: Data) -> Data:
  store = []

  for serial_number in data.body.serial_numbers:
    validations = [
      await validate_length(
        serial_number=serial_number,
        bounds=data.body.char_n_bounds,
      ),
      await validate_print_year(
        serial_number=serial_number,
        bounds=data.body.year_bounds,
      ),
      await validate_uppercase_alpha_chars(
        serial_number=serial_number,
      ),
    ]
    validations = sum(validations)
    if validations != 0:
      continue
    store.append(serial_number)

  currency = Currency(serial_numbers=store)
  data.currency = currency
  return data


async def get_denominations(data: Data) -> Data:
  store = []

  for serial_number in data.currency.serial_numbers:
    denomination = serial_number[7:-1]
    try:
      denomination = int(denomination)
    except ValueError:
      denomination = 0

    if denomination in data.body.valid_denominations:
      store.append(denomination)

  data.currency.denominations = store
  data.currency.total = sum(store)
  return data


async def get_response(data: Data) -> models.Response:
  data = f'''
    input: {asdict(data.body)} 
    output: 
      currency: {asdict(data.currency)}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  body = asdict(request.data.body)
  body = Body(**body)
  data = Data(body=body)
  request = None
  data = await validate_serial_numbers(data=data)
  data = await get_denominations(data=data)
  data = await get_response(data=data)
  return data

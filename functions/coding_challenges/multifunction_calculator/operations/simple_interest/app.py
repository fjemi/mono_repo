from dataclasses import dataclass, field, fields
from typing import List, Dict


@dataclass
class Data:
  principal: float | None = None
  rate: float | None = None
  time: float | None = None
  time_ordinal: str = 'years'
  accrued: float | None = None
  total_accrued: float = None


def calculate_principal(data: Data) -> Data:
  '''
  description: 
    Calculate principal amount given rate, time, and amount accrued
    Formula: P = A / (1 + rt)
  '''
  # Accrued over principal fraction
  denomator = data.accrued / (1 + data.rate * data.time)
  data.principal = data.accrued / denomator
  return data


def calculate_rate(data: Data) -> Data:
  '''
  description: 
    Calculate rate given principal amount, time, and amount accrued
    Formula: r = (A/P - 1) / t
  '''
  # Accrued over principal fraction
  fraction = data.accrued / data.principal
  data.rate = (fraction - 1) / data.time
  return data


def calculate_time(data: Data) -> Data:
  '''
  description: 
    Calculate time given the principal ammount, rate, and amount accured
    Formula: t = (A/P - 1) / r
  '''
  # Accrued over principal fraction
  fraction = data.accrued / data.principal
  data.time = (fraction - 1) / data.rate
  return data


def calculate_accrued(data: Data) -> Data:
  '''
  description: 
    Calculate amount accrued given the principal amount, rate, and time
    Formula: A = P(1 + rt)
  '''
  data.accrued = data.principal * (1 + data.rate * data.time)
  return data


def calculate_total_accrued(data: Data) -> Data:
  '''
  description: 
    Calculate total accrued amount; principal plus interest
    Formula: Total = P + A
  '''
  data.total_accrued = data.principal + data.accrued
  return data


def get_function_name(data: Data) -> Data | None:
  '''
  description:
    Gets the name of the function needed to process the given inputs.
  '''

  for data_class_field in fields(data.inputs):
    value = getattr(data.inputs, data_class_field.name)
    if value is not None:
      continue
    # Value of first field with a null value needs to be calculated.
    # Assumes this is the only null field value.
    function_name = f'calculate_{data_class_field.name}'
    return function_name
  return None


# data = Data()
# # data = main(data)
# print(data)

# import caclulator
# calculator_data = caclulator.Data(inputs=data)
# print(calculator_data)

# function_name = get_function_name(data=calculator_data)
# print(function_name)


#!usr/bin/env python3

from dataclasses import dataclass, fields
from typing import List


@dataclass
class Inputs:
  force: float | None = None
  mass: float | None = None
  acceleration: float | None = None


@dataclass
class Data:
  inputs: Inputs | None = None
  operation: str | None = None


async def calculate_force(data: Data) -> Data:
  '''
  description:
    Calculates force using the equation for Newton's second law of motion
  '''
  data.inputs.force = data.inputs.mass * data.inputs.acceleration
  return data


async def calculate_mass(data: Data) -> Data:
  '''
  description:
    Calculates mass using the equation for Newton's second law of motion
  '''
  data.inputs.mass = data.inputs.force / data.inputs.acceleration
  return data


async def calculate_acceleration(data: Data) -> Data:
  '''
  description:
    Calculates acceleration using the equation for Newton's second law of motion
  '''
  data.inputs.acceleration = data.inputs.force / data.inputs.mass
  return data


OPERATIONS = {
  'newtons_second_law.force': calculate_force,
  'newtons_second_law.mass': calculate_mass,
  'newtons_second_law.acceleration': calculate_acceleration,
}


async def main(
  inputs: dict,
  operation: str,
) -> Data:

  inputs = Inputs(**inputs)
  data = Data(inputs=inputs, operation=operation)
  operation = OPERATIONS[operation]
  data = await operation(data=data)
  return data


if __name__ == '__main__':
  import asyncio


  inputs = {
    'force': 1,
    'mass': 1,
  }
  result = asyncio.run(main(
    inputs=inputs,
    operation='newtons_second_law.acceleration',
  ))
  print(result)


  # # Switcher to pick equation based off missing data
  # switcher = dict(
  #   force=calculate_force,
  #   mass=calculate_mass,
  #   acceleration=calculate_acceleration,
  # )
  # # Caculate the missing value
  # calculated_value = None
  # for field in fields(data):
  #   value = getattr(data, field.name)
  #   if value is not None:
  #     continue
  #   calculated_value = switcher[field.name](data=data)
  #   setattr(data, field.name, calculated_value)
  # # Return solution
  # if calculated_value is not None:
  #   return data

  # # Handle no missing data; verify first equation, F = ma
  # name = list(switcher.keys())[0]
  # value = getattr(data, name)
  # calculated_value = switcher[name](data)
  # assert calculated_value == value


# d = [
#   Data(6, 2, 3),
#   Data(1, 2, None),
#   Data(1, None, 2),
#   Data(1, 2, 3),
# ]
# for data in d:
#   data = main(data)
#   print(data)

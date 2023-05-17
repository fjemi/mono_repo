from dataclasses import dataclass, fields
from typing import List


@dataclass
class Data:
  force: float | None = None
  mass: float | None = None
  acceleration: float | None = None


def calculate_force(data: Data) -> float:
  '''
  description:
    Calculates force using the equation for Newton's second law of motion
  '''
  return data.mass * data.acceleration


def calculate_mass(data: Data) -> float:
  '''
  description:
    Calculates mass using the equation for Newton's second law of motion
  '''
  return data.force / data.acceleration


def calculate_acceleration(data: Data) -> float:
  '''
  description:
    Calculates acceleration using the equation for Newton's second law of motion
  '''
  return data.force / data.mass


def main(data: Data | dict | str) -> Data:
  '''Orchestration function that executes the function within this module'''
  data = type_handler.main(data=data, data_class=Data)
  # Switcher to pick equation based off missing data
  switcher = dict(
    force=calculate_force,
    mass=calculate_mass,
    acceleration=calculate_acceleration,
  )
  # Caculate the missing value
  calculated_value = None
  for field in fields(data):
    value = getattr(data, field.name)
    if value is not None:
      continue
    calculated_value = switcher[field.name](data=data)
    setattr(data, field.name, calculated_value)
  # Return solution
  if calculated_value is not None:
    return data

  # Handle no missing data; verify first equation, F = ma
  name = list(switcher.keys())[0]
  value = getattr(data, name)
  calculated_value = switcher[name](data)
  assert calculated_value == value


# d = [
#   Data(6, 2, 3),
#   Data(1, 2, None),
#   Data(1, None, 2),
#   Data(1, 2, 3),
# ]
# for data in d:
#   data = main(data)
#   print(data)

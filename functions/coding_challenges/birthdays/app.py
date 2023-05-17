#!/usr/bin/env python3

from typing import List
from datetime import datetime
from dataclasses import dataclass, field

from shared.type_handler import app as type_handler


DATE_FORMAT: str = '%Y%m%d'


@dataclass
class BirthDate:
  weekday: str = None
  date: str = None


@dataclass
class Data:
  '''
  attributes:
    birth_date: The day an individual was born
    birthdays: List of birth_dates the individuals has had
    weekday_counts: Counts birthdays by weekday
  '''
  birth_date: str = None
  birthdays: List[BirthDate] = field(default_factory=lambda: [])
  ending_year: int = field(
    default_factory=lambda: int(datetime.utcnow().strftime('%Y')))
  weekday_counts: dict = field(default_factory=lambda: {})
  date_format: str = field(default_factory=lambda: DATE_FORMAT)


def get_birthdays(data: Data) -> Data:
  '''Collects an individuals birthdays since their birth_date'''
  # Convert string to datetime object
  birthday = datetime.strptime(data.birth_date, data.date_format)
  # Set the year the individual was born in
  # and their age
  year = int(data.birth_date[:4])
  age = data.ending_year - year
  # Account for ending and birth year being the same
  if age == 0:
    age = 1
  for i in range(age):
    year = year + 1
    days = 365
    # Account for leap years
    if year % 4 == 0:
      days = 366
    # Step to next birthday. Use seconds for calculations
    seconds_in_year = days * 86400
    seconds_since_epoch = birthday.timestamp()
    seconds = seconds_since_epoch + seconds_in_year
    # Format birth/week days
    birthday = datetime.fromtimestamp(seconds)
    birthday_str = birthday.strftime(data.date_format)
    weekday = birthday.strftime('%A')
    data.birthdays.append(BirthDate(date=birthday_str, weekday=weekday))
  return data


def get_weekday_counts(data: Data) -> Data:
  '''Count birthdays by weekday'''
  store = {}
  for i in range(len(data.birthdays)):
    weekday = data.birthdays[i].weekday.lower()
    if weekday in store.keys():
      store[weekday] += 1
      continue
    store[weekday] = 1
  data.weekday_counts = store
  return data


def main(data: Data | dict | str) -> Data:
  '''Orchestration function that executes the function within this module'''
  data = type_handler.main(data=data, data_class=Data)
  data = get_birthdays(data)
  data = get_weekday_counts(data)
  return data


def example() -> None:
  data = '''
    birth_date: '20220101'
  '''
  data = main(data=data)
  print(data)


if __name__ == '__main__':
  example()

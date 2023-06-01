#!/usr/bin/env python3

from typing import List
from math import floor
import dataclasses as dc
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Body:
  expenditures: List[float | int] | None = None
  trailing_days: int = 0


@dc.dataclass
class Result:
  number: int = 0
  value: str = ''


@dc.dataclass
class Window:
  '''
  Attributes:
    i: Starting index of trailing day expenses for the current day
    j: Ending index of trailing day expenses for the current day
    current: Index of the current days expense
    median: The median of the trailing day expenses
  '''
  trailing: List[float | int] = dc.field(default_factory=lambda: [])
  median: float | int = 0
  current: float | int = 0


@dc.dataclass
class Data:
  '''
  Attributes:
    expenditures: Daily expenditures for a span of `n` days
    trailing_days: The number of trailing days
    windows: List of current/trailing day expenses
    notifications: Store data resulting in a notification
  '''
  body: Body | None = None
  windows: List[Window] = dc.field(default_factory=lambda: [])
  notifications: List[Window] = dc.field(default_factory=lambda: [])


async def get_notifications_for_windows(data: Data) -> List[Window]:
  '''Determine if a notification is needed for windows'''
  data.notifications = []

  n = len(data.windows)
  for k in range(n):
    data.windows[k].median = await calculate_median(data.windows[k].trailing)
    # Aggregate data to determine if a notification is needed
    # The current expense exceeds trailing expenses median doubled
    # data.windows[k].current = data.body.expenditures[data.windows[k].current]
    check = data.windows[k].median * 2 <= data.windows[k].current
    if check is False:
      continue
    # Add window to nodata = notification store
    data.notifications.append(data.windows[k])
  return data


async def calculate_median(numbers: List[float | int]) -> float | int:
  '''Calculate the median for a list of numbers'''
  numbers.sort()
  n = len(numbers)

  # Empty list of numbers
  if n == 0:
    return 0
  # Even lengthened list of numbers
  if n % 2 != 0:
    index = floor(n / 2)
    return numbers[index]
  # Odd lengthened list of numbers
  if n % 2 == 0:
    start = floor(n / 2) - 1
    end = start + 1
    print(numbers, start, end)
    return (numbers[start] + numbers[end]) / 2


async def get_trailing_windows(data: Data) -> List[Window]:
  '''Get list of current and trailing expenses windows'''
  n = len(data.body.expenditures)
  data.windows = []
  for i in range(n):
    # Expenses between `i` and `j` form the trailing window
    j = i + data.body.trailing_days
    # No more windows
    if j >= n:
      break
    current = data.body.expenditures[j]
    trailing = data.body.expenditures[i:j]
    window = Window(current=current, trailing=trailing)
    data.windows.append(window)
  return data


async def get_response(data: Data) -> dict:
  return {'windows': data.notifications}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  expenditures: List[float | int] | None = None,
  trailing_days: int | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await get_trailing_windows(data=data)
  data = await get_notifications_for_windows(data=data)
  data.notifications = [dc.asdict(x) for x in data.notifications]
  data = await get_response(data=data)
  return data

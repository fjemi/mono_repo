#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List
import yaml

from api import models


@dataclass
class Stock:
  days: List[int] = field(default_factory=lambda: [])
  prices: List[int] = field(default_factory=lambda: [])
  profit: int = 0


@dataclass
class Body(models.Body):
  prices: List[int] | None = None
  stock: Stock | None = None


@dataclass
class Data(models.Data):
  body: Body | None = None


@dataclass
class Request(models.Request):
  data: Data | None = None


@dataclass
class Data:
  body: Body | None = None
  max_profit: List[Stock] = field(default_factory=lambda: [])


SWITCH = {
  
}


async def check_profit_and_store_stock(
  data: Data,
) -> List[Stock] | None:
  if len(data.max_profit) == 0:
    store = [data.stock]
    return store

  previous_stock = data.max_profit[-1]
  if data.stock.profit < previous_stock.profit:
    return data.max_profit

  if data.stock.profit > previous_stock.profit:
    store = [data.stock]
    return store

  if data.stock.profit == previous_stock.profit:
    data.max_profit.append(data.stock)
    return data.max_profit

  return None


async def get_max_profit(data: Data) -> List[Stock]:
  prices_n = len(data.body.prices)
  for i in range(prices_n - 1):
    for j in range(i +1, prices_n):
      profit = data.body.prices[j] - data.body.prices[i]
      data.stock = Stock(
        days=[i, j],
        prices=[data.body.prices[i], data.body.prices[j]],
        profit=profit,
      )
      data.max_profit = await check_profit_and_store_stock(data=data)
  return data


async def get_response(data: Data) -> models.Response:
  stock = data.max_profit[0]
  profit = stock.profit
  data = f'''
    input: {asdict(data.body)}
    output: 
      profit: {profit}
  '''
  data = yaml.safe_load(data)
  data = models.Response(data=data)
  return data


async def main(request: Request) -> models.Response:
  data = Data(body=request.data.body)
  request = None
  data = await get_max_profit(data=data)
  data = await get_response(data=data)
  return data

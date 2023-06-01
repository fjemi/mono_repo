#!/usr/bin/env python3

import dataclasses as dc
from typing import List
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Stock:
  days: List[int] = dc.field(default_factory=lambda: [])
  prices: List[int] = dc.field(default_factory=lambda: [])
  profit: int = 0


@dc.dataclass
class Body:
  prices: List[int] | None = None
  stock: Stock | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  max_profit: List[Stock] = dc.field(default_factory=lambda: [])


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


async def get_response(data: Data) -> dict:
  stock = data.max_profit[0]
  profit = stock.profit
  return {'profit': profit}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  prices: List[int] | None = None,
  stock: Stock | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await get_max_profit(data=data)
  data = await get_response(data=data)
  return data
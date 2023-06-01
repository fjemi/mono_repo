#!/usr/bin/env python3

import dataclasses as dc
from typing import Any
import yaml
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Query_Params:
  data: str | None = None


@dc.dataclass
class Body:
  data: Any | None = None


@dc.dataclass
class Data:
  query_params: Query_Params | None = None
  body: Body | None = None


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  data: Any | None = None,
) -> None:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={
      'query_params': Query_Params,
      'body': Body,
    },
    main_data_class=Data,
  )
  data = dc.asdict(data)
  try:
    data = yaml.dump(
      data,
      indent=2,
      default_flow_style=None,
    )
  except Exception:
    pass
  print(data)

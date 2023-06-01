import dataclasses as dc


@dc.dataclass
class Data:
  pass


def main(data: Data | dict) -> Data:
  return data

# collect all yml files
# collect all dependencies
# pipenv install all the dependencies

from dataclasses import dataclass
from typing import Union

@dataclass
class Data:
    pass


def get_dependencies(data: Union[Data, dict]):
    if isinstance(data, dict):
        data = Data(**data)
    pass
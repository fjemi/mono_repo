# Standard
import os
from os.path import exists, dirname, abspath, join
from dataclasses import dataclass, field
from typing import List, Union, Optional
from importlib import import_module
import importlib.util
import sys
# External
from box import Box


FILE_PATH = abspath(__file__)
FILE_DIR = dirname(FILE_PATH)


@dataclass
class Data:
    path: str = None
    modules: List[str] = field(default_factory=lambda: [])
    globals_namespace: dict = field(default_factory=lambda: globals())


def get_module_list(data: Union[Data, dict]) -> Optional[Data]:
    if not exists(data.path):
        return None

    if isinstance(data, dict):
        data = Data(**data)

    # Iterate over the files and folders to find python scripts
    for item in os.listdir(data.path):
        path = join(data.path, item)
        # Ignore files or this files parent directory
        if os.path.isfile(path) or path == FILE_DIR:
            continue
        # Add module and its path
        data.modules.append(Box(
            name=item,
            path=join(path, f'{item}.py'), ))
    return data


def add_modules_to_globals(data: Union[Data, dict]) -> Optional[Data]:
    if data is None:
        return None

    if isinstance(data, dict):
        data = Data(**data)

    # Add the main function of each module to globals
    for module in data.modules:
        spec = importlib.util.spec_from_file_location(module.name, module.path)
        foo = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = foo
        spec.loader.exec_module(foo)
        data.globals_namespace[module.name] = getattr(foo, module.name)
    return data


def get_nested_modules(data: Union[Data, dict]) -> Optional[Data]:
    if isinstance(data, dict):
        data = Data(**data)

    data = get_module_list(data)
    data = add_modules_to_globals(data)
    return data


def example() -> None:
    path = '/home/femij/Desktop/mono_repo/python/utils/get_nested_modules/test'
    data = Data(path=path)
    data = get_nested_modules(data)
    # Test function is added to globals
    print(globals()['test']())


if __name__ == '__main__':
    example()

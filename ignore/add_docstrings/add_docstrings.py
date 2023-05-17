# Standard
from dataclasses import dataclass, field
from typing import List, Union
# External
from box import Box
# Internal
# from shared.exception_handler.exception_handler import exception_handler


@dataclass
class Data:
    functions: List[dict] = field(default_factory=lambda: [])
    data: List[dict] = field(default_factory=lambda: [])
    tests: List[dict] = field(default_factory=lambda: [])
    links: List[dict] = field(default_factory=lambda: [])


# @exception_handler
def add_docstrings(data: Union[Data, dict]):
    if isinstance(data, dict):
        data = Data(**data)

    def _doc(func):
        docstrings = None
        # Get docstrings for the function
        for docs in data.functions:
            if docs.name == func.__name__:
                docstrings = docs
                break
        
        # Do nothing if there are no docstrings
        if docstrings is None:
            return func

        # Set parameters
        if docstrings.parameters:
            docstrings.parameters = data.data
        # Set docstrings
        func.__doc__ = docstrings
        return func
    return _doc

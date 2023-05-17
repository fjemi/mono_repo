# # Module to test
# import exception_handler as module
# from shared.main import get_yml_data
# # External
# from typing import List
# from dataclasses import dataclass, asdict, field
# import json


# @dataclass(order=True)
# class Data:
#   tests: List[dict] = field(default_factory=lambda: 
#     get_yml_data(dict(path=__file__, top_level_key='tests')))
#   failed: List['str'] = field(default_factory=lambda: [])


# # @module
# def add(a: int, b: int) -> int:
#   '''Function decorated with the exception handler (module) for testing'''
#   return a + b


# def exception_handler_test(data: Data = Data()) -> None:
#   '''
#   Description
#     Run tests defined in a YAML against each function within a module
#   Parameters
#     tests: A list of tests to run
#     failed: A list of failed tests
#   Returns
#     None
#   '''
#   for test in data.cases:
#     # Load function and excute with inputs
#     function = getattr(module, test.function)
#     output = function(test.input)
#     # Check that function outputs as expected
#     assert output == test.output

# Internal
import add_docstrings
from shared.get_yml_data.get_yml_data import get_yml_data
# Standard
import json
import dataclasses as dc
from typing import List


@dc.dataclass
class Store:
    passed: List['str'] = dc.field(default_factory=lambda: [])
    failed: List['str'] = dc.field(default_factory=lambda: [])


def add_docstrings_test() -> None:
    
    tests = get_yml_data({'path': __file__, 'top_level_key': 'tests'})
    store = Store()

    # Execute tests defined in YML file
    for test in tests:
        # Set function to test
        function = getattr(add_docstrings, test.function)

        @function(test.input)
        def test_function():
            '''test for docstrings'''
            return {}

        # Execute function with test data
        output = test_function.__doc__
        result = output == test.output

        # Add test to store based on result
        if result is True:
            store.passed.append({'function': test.function, 'test': test.description})
        else:
            store.failed.append({'function': test.function, 'test': test.description})
    
    print(json.dumps(dc.asdict(store), indent=2))
    # List of failed test should be empty if all tests pass
    assert len(store.failed) == 0
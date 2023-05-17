# Internal
import get_yml_data as module
from shared.main import unit_tests


def get_yml_data_test() -> None:
    '''Run tests defined within a YAML file'''
    filepath = __file__
    tests = dict(filepath=filepath, module=module)
    unit_tests(tests=tests)

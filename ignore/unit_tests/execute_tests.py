from shared.unit_tests.models import Tests, Case
from typing import List
from dataclasses import asdict, is_dataclass
from pprint import pprint
from json import dumps

def execute_tests(tests: Tests) -> None:
  '''
  Summary
    Runs a list of tests
  Parameters
    tests: List[Test] = List of ests to run
    module: ModuleType = Module containing functions to test
  Returns
    List of failed tests
  '''
  for i in range(len(tests.cases)):
    case = tests.cases[i]
    # Load the module
    # module = importlib(path_to_module)
    # Set function from the module to test
    function = getattr(tests.module, case.function)
    # Function should produce expected output
    # when provided inputs from the yaml file
    output = function(case.inputs)
    
    # Format output
    output_type = type(output).__name__ 
    # Convert dataclasses to dictionaries
    if is_dataclass(output):
      output_type = 'dataclass'
      output = asdict(output)
    
    # Check that ouput and output type are as expected
    case.passed['output_check'] = output == case.output
    if not isinstance(case.output_type, list):
      case.output_type = [case.output_type]
    case.passed['output_type_check'] = output_type in case.output_type
    # Handle failed tests
    if False not in list(case.passed.values()):
      continue
    result = {
      'description': case.description, 
      'output': output, 
      'expected': case.output, }
    # pprint(result)
    print(dumps(result, indent=2))
    assert output == case.output


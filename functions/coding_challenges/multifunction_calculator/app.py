# def FMA():
#     print ("This function calculates the force of an object given its acceleration and mass")
#     print ("\n")

#     massinput = 0.0
#     accelerationinput = 0.0
    
# # get the mass
#     while True:
#         try:
#             massinput = float(input("What is the mass of the object (kg): "))
#         except ValueError:
#             print ("Not a number! Try again.")
#             print ("\n")
#             continue
#         else:
#             break

# # get the velocity  
#     while True:
#         try:
#             accelerationinput = float(input("What is the acceleration of the object (m/s): "))
#             print ("\n")
#         except ValueError:
#             print ("Not a number! Try again.")
#             print ("\n")
#             continue
#         else:
#             break
    
#     force = massinput * accelerationinput**2
    
#     print ("The force an object accelerating at %d with a mass of %d is %.2f" % (accelerationinput, massinput, force))


# def Interest():
#     print ("This function calculates interest given the principal, rate, and time")
#     print ("\n")
    
#     pinput = 0.0
#     rinput = 0.0
#     time = 0.0
#     accrued = 0.0
    
# # get the Principal
#     while True:
#         try:
#             pinput = float(input("What is the Principal ($): ")) 
#         # check if user input is a number
#         except ValueError:
#             print ("Not a number! Try again.")
#             print ("\n")
#             continue
#         else:
#             # check is user input is less than 0
#             if (pinput < 0):
#                 print ("Principal cannot be negative! Try again.")
#                 print ("\n")
#                 continue
#             else:
#                 break
                
# # get rate rate                
#     while True:
#         try:
#             rinput = float(input("What is the rate (%): ")) 
#         # check if user input is a number
#         except ValueError:
#             print ("Not a number! Try again.")
#             print ("\n")
#             continue
#         else:
#             # check is user input is greater than 0 or less than 1
#             if (rinput < 0 or rinput > 1):
#                 print ("Enter a rate between 0 and 1! Try again.")
#                 print ("\n")
#                 continue
#             else:
#                 break
                
# # get the time                
#     while True:
#         try:
#             tinput = float(input("What is the time (months): ")) 
#         # check if user input is a number
#         except ValueError:
#             print ("Not a number! Try again.")
#             print ("\n")
#             continue
#         else:
#             # check is user input is less than 0
#             if (tinput < 0):
#                 print ("Enter a valid time in months! Try again.")
#                 print ("\n")
#                 continue
#             else:
#                 break
                
# # simple interest A = P(1 + rt)
#     accrued = pinput * (1 + rinput * tinput)

#     print ("The total amount accrued is %.2f " % (accrued))


# function = {"FMA()": "Force","Interest()":"Interest"}

# print ("This is a calculator. Please choose a function.")

# for key in function:
#     print ("%s Function: %s" % (function[key], key))
    
# print ("What function would you like to use? ")


# FMA()

# Interest()


# number = get_input('test: ')
# print(number)

# from os import walk

# test = walk('.')
# for t in test:
#   print(t)operation_groups

# import yaml
# data = 'test: ${PWD}'
# data = yaml.safe_load(data)
# print(data)

# import os
# for key in os.environ.keys():
#   print(key)

# print(os.environ['WORKDIR'])

# import dotenv
# env_path = __file__.replace('.py', '.env')
# env = dotenv.dotenv_values(env_path)
# print(env)


#------------------

from typing import List, Dict, Any, Callable
from dataclasses import dataclass, fields
import sys
import yaml
import json

import get_operations.app as get_operations


@dataclass
class Data:
  operations: Dict[str, Any] | None = None
  operations_by_group: Dict[str, List[str]] | None = None
  operation_symbols: Dict[str, str] | None = None


def json_to_yaml(data: Dict):
  # data = yaml.safe_load(data)
  data = yaml.safe_dump(data, indent=2, default_flow_style=False)
  data = data.replace('_', ' ')
  data = data.title()
  print(data)


def list_operations_by_group(operations: Dict) -> Dict[str, List[str]]:
  '''
  description: Returns a dictionary with keys being operation groups and values
    being lists of operations
  '''
  groups = {}
  for key in operations.keys():
    name = key.split('.')
    group_name = name[0]
    operation_name = name[1]
    if group_name not in groups.keys():
      groups[group_name] = []
    groups[group_name].append(operation_name)
  return groups


def get_input(message: str, is_number: bool = False) -> str | float:
  '''
  description: Returns user inputs from the command. Handles closing the 
    application, and casts strings to numbers for operation calculations.
  '''
  data = input(message)
  # Exit without traceback error
  if data.lower() == 'exit':
    sys.exit('Closing Application')
  # Convert string to number
  if is_number:
    return float(data)
  return data


def get_operation_abbreviation(operation_key: str) -> str:
  '''
  description: Returns the abbreviation for an operation key
  '''
  abbreviation = ''
  group_operation_name = operation_key.split('.')
  operation_name = group_operation_name[1]
  words = operation_name.split('_')
  for word in words:
    char = word[0].upper()
    abbreviation += char
  return abbreviation


def get_operation_symbols(operation_keys: List[str]) -> Dict[str, str]:
  '''
  description: Returns the symbols for operations. The symbols are a combination
    of the operation's abbreviation and number of occurances of the abbreviation
  notes: Symbols can be used to shorten routes for urls or for calling 
    operations via the command line
  '''
  occurances = []
  store = {}

  for operation_key in operation_keys:
    abbreviation = get_operation_abbreviation(operation_key=operation_key)
    count = occurances.count(abbreviation)
    occurances.append(abbreviation)
    symbol = f'{abbreviation}_{count}'
    store[symbol] = operation_key
  return store


def main(data: Data = None):
  '''
  description: 
  '''
  data = Data()
  operations_data = get_operations.Data(
    file_path=__file__, 
    operations_directory_name='operations',
  )
  data.operations = get_operations.main(data=operations_data)
  data.operations_by_group = list_operations_by_group(
    operations=data.operations)
  data.operation_symbols = get_operation_symbols(
    operation_keys=list(data.operations.keys()))
  return data


data = main()

'''
Enter a symbol to get an operation

'''

def cli_get_symbol(operation_symbols: Dict[str, str]) -> str | None:
  '''
  description: 
  '''
  print('Starting Application')
  while True:
    message = 'Pick an operation by entering its symbol, or enter "exit" to quit\n'
    print(operation_symbols)
    # Symbols are uppercase
    cli_input = get_input(message).upper()
    # If the symbol is not entered correctly
    if cli_input not in list(operation_symbols.keys()):
      continue
    return cli_input


def cli_get_operation_from_symbol(symbol: str) -> Dict[Callable, Any]:
  ''''''
  operation = None


  return operation


def add_symbol_to_operations_by_group(
  operations_by_group: Dict[str, List[str]],
  operation_symbols: Dict[str, str],
) -> Dict[str, List[Dict[str, str]]]:
  ''''''
  for group in operations_by_group.keys():
    operations = operations_by_group[group]
    for operation in operations:
      name = f'{group}.{operation}'

  return operations_by_group


test = json_to_yaml(data.operations_by_group)
print(test)
# print(data.operation_symbols)
# test = json_to_yaml(data.operation_symbols)
# print(test)



cli_symbol = cli_get_symbol(operation_symbols=data.operation_symbols)
cli_operation_key = data.operation_symbols[cli_symbol]
cli_operation = data.operations[cli_operation_key]

print(cli_operation)

json_data = {}
for field in fields(cli_operation.data):
  if field is None:
    continue
  message = f'\x20{field.name}: '
  is_number = False
  if field.type == float | None:
    is_number = True
  json_data[field.name] = get_input(message, is_number=is_number)
print(json_data)
operation_data = cli_operation.data(**json_data)
print(cli_operation.function(data=operation_data))


test = json_to_yaml(json_data)
print(test)
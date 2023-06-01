import os
import dataclasses as dc
from typing import List, Union


@dc.dataclass 
class Data:
  '''
  Description
    Store data for getting a list of files within a directory
  Attributes
    path: Directory to get files from
    extensions: Filter for files with theses extensions
    wildcards: Filter file names/paths using wildcards
  '''
  directory: str = None
  extensions: List[str] = dc.field(default_factory=lambda: [])
  wildcards: List[str] = dc.field(default_factory=lambda: [])
  files: List[str] = dc.field(default_factory=lambda: [])


def get_files_in_directory(data: Union[Data, dict]) -> dict:
  '''Gets all of the files within a directory'''
  if isinstance(data, dict):
    data = Data(**data)

  data.files = []

  if os.path.exists(data.directory) is False:
    return data

  # List directories, subdirectories, and files
  for path, subdirs, files in os.walk(data.directory):
    for name in files:
      file_path = os.path.join(path, name)
      data.files.append(file_path)
  return data


def main(data: Union[Data, dict]) -> dict:
  if isinstance(data, dict):
    data = Data(**data)

  data = get_files_in_directory(data=data)
  data = perform_checks(data=data)
  return {'files': data.files}


def perform_checks(data: Union[Data, dict]) -> Data:
  '''
  Filter out file paths that fail checks
  '''  
  if isinstance(data, dict):
    data = Data(**data)

  for i in reversed(range(len(data.files))):
    checks = [
      extension_check(extensions=data.extensions, file_path=data.files[i]),
      wildcard_check(wildcards=data.wildcards, file_path=data.files[i]), 
    ]
    # Keep file paths that pass all of the checks
    if sum(checks) == len(checks):
      continue
    # Filter out file paths that fail one or more checks
    del data.files[i]
  return data


def wildcard_check(wildcards: List[str], file_path: str) -> bool:
  '''Check if the file path has a matching wildcard'''
  # Handle no check
  if wildcards is None or wildcards == []:
    return True
  for wildcard in wildcards:
    if file_path.find(wildcard) > -1:
      return True
  return False


def extension_check(extensions: List[str], file_path: str) -> bool:
  '''Check if the file has a matching extension'''
  # Handle no check
  if extensions is None or extensions == []:
    return True
  # Get file extension and check if it is in list of extensions
  file_extension = os.path.splitext(file_path)[1]
  if file_extension in extensions:
    return True
  return False


if __name__ == '__main__':

  data = Data(directory='./app', wildcards=['test.yml'])
  print(main(data))

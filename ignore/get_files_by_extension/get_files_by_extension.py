# Standard 
import os
from dataclasses import dataclass, field
from typing import List, Union, Optional
# Standard 
from functions.exception_handler.exception_handler import exception_handler


@dataclass
class Data:
  directories: List[str] = field(default_factory=lambda: [])
  extensions: List[str] = field(default_factory=lambda: [])
  files: List[str] = field(default_factory=lambda: [])


@exception_handler
def get_files_by_extension(data: Union[Data, dict]) -> Optional[Data]:
  '''Searches a directory and retrieves files with certain extensions'''
  if isinstance(data, dict):
    data = Data(**data)

  # Check directories for files with matching extensions
  for directory in data.directories:
    for file in os.listdir(directory):
      extension = os.path.splitext(file)[1]
      if extension in data.extensions:
        data.files.append(f'{directory}/{file}')
  return data

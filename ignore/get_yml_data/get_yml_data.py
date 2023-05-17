# Standard
from typing import Union, Dict, Optional
import dataclasses as dc
from os.path import exists, abspath, expandvars, dirname
import sys
# External
import yaml
from box import Box
# Internal
# from shared.main import exception_handler


@dc.dataclass
class Data:
    '''
    Description
        Stores data related to a yaml file
    Attributes
        - path: The path to a `.py` or `.yml` file  
        - text: Text from the YML file
        top_level_key: A key at the top level of the yaml file to return \
        the value of
        - yml: The data from the yaml file
    '''
    path: str = ''
    text: str = None
    yml: dict = None
    top_level_key: str = None


# @exception_handler
def set_path(data: Union[Data, Dict]) -> Optional[Data]:
    '''
    '''
    # Convert dict to dataclass
    if isinstance(data, dict):
        data = Data(**data)

    # Do nothing if path directs to yml file
    if data.path.find('.yml') != -1:
        return data

    # Set path if path directs to python file by replacing text in path
    replace_text = [
        Box(replace='.py', value='.yml'),
        Box(replace='test_', value=''),
        Box(replace='_test', value=''), ]
    for text in replace_text:
        data.path = data.path.replace(text.replace, text.value)
    
    return data


# @exception_handler
def set_env_vars(data: Union[Data, dict]) -> Optional[Data]:
    if data is None:
        return None

    # Convert dict to dataclass
    if isinstance(data, dict):
        data = Data(**data)
    # Map text to defined variables
    mapper = Box(WORKING_DIR=dirname(data.path))
    for key in mapper:
        data.text = data.text.replace(key, mapper[key])
    # Set environment variables
    data.text = expandvars(data.text)
    return data


# @exception_handler
def get_yml_data(data: Union[Data, Dict]) -> Optional[dict]:
    # Convert dict to dataclass
    if isinstance(data, dict):
        data = Data(**data)

    data = set_path(data)

    # Get and return yml data
    with open(data.path, 'r') as file:
        data.text = file.read()
        data = set_env_vars(data)
        data.yml = Box(yaml.safe_load(data.text))
    # Only return data associated with a top level key
    if data.top_level_key:
        return data.yml[data.top_level_key]

    return data.yml

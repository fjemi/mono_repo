import dacite
from typing import List, Dict
from dataclasses import dataclass, field, fields
from os import path

from shared.untested_get_environment import app as get_environment


ENV = get_environment.main(file_path=__file__)



BINARY_MAP = {
  True: 'yes',
  False: 'no',
  1: 'yes',
  0: 'no',
  'yes': 'yes',
  'no': 'no',
}


@dataclass
class NodeCounts:
  start: List[Dict[str, str]] = field(default_factory=lambda: [])
  end: List[Dict[str, str]] = field(default_factory=lambda: [])
  operation: List[Dict[str, str]] = field(default_factory=lambda: [])
  condition: List[Dict[str, str]] = field(default_factory=lambda: [])
  inputoutput: List[Dict[str, str]] = field(default_factory=lambda: [])
  subroutine: List[Dict[str, str]] = field(default_factory=lambda: [])


@dataclass
class Font:
  size: float = 14
  weight: str = 'regular'
  color: str = 'black'


@dataclass
class Connection:
  node_name: str | None = None
  direction: str | None = None
  binary: bool | int | str = None
  binary_text: str | None = None
  _type: str | None = None
  stroke: str | None = None
  stroke_width: float | None = None
  arrow_end: str | None = None
  # font: Font = field(default_factory=lambda: Font())


@dataclass
class Node:
  name: str | None = None
  _type: str | None = None
  text: str | None = None
  url: str | None = None
  connections: List[Connection] | Connection = field(default_factory=lambda: [])
  # fill: str | None = None
  # font: Font = field(default_factory=lambda: Font())

  
@dataclass
class Data:
  nodes: List[Node] | Node = field(default_factory=lambda: [])
  nodes_dict: Dict[str, Node] = field(default_factory=lambda: {})
  nodes_string: str = ''
  connections_string: str = ''
  string: str = ''
  directory_path: str = ENV.DATA_DIR
  file_name: str = 'flowchart.txt'


def setup_data(data: Data) -> Data:
  if isinstance(data, Data):
    return data
  if isinstance(data, dict):
    return dacite.from_dict(Data, data)


def setup_nodes_string(data: Data) -> Data:
  node_counts = NodeCounts()
  node_types = [key.name for key in fields(node_counts)]

  for node in data.nodes:
    # Raise error if the node type satisfies these conditions
    exception_conditions = [
      node._type is None,
      node._type == '',
      node._type == 'start' and len(node_counts.start) == 1,
      node._type == 'end' and len(node_counts.end) == 1,
      node._type not in node_types,
      node.name is None or node.name == '',
    ]
    if 1 in exception_conditions:
      raise RuntimeError

    # Get node type count 
    nodes_by_type = getattr(node_counts, node._type)
    nodes_by_type.append(node.name)
    setattr(node_counts, node._type, nodes_by_type)

    # Fill in missing details
    if node.text is None or node.text == '':
      node.text = node.name
    if node.url is not None:
      node.url = f':>{node.url}'
    else:
      node.url = ''

    # # Set the node string
    node_string = f'{node.name}=>{node._type}: {node.text}{node.url}\n'
    data.nodes_string = data.nodes_string + node_string
    data.nodes_dict[node.name] = node

  return data


def setup_connections_string(data: Data) -> Data:
  for node in data.nodes:
    for connection in node.connections:    
      # Format the connection details
      connection_details = ''

      # Format binary and non-binary connections
      if connection.binary is not None:
        connection.binary = BINARY_MAP[connection.binary]
        connection.binary = f'{connection.binary},'
      else:
        connection.binary = ''

      if connection.binary_text is not None:
        connection.binary.replace(',', f'@{connection.binary_text},')

      # Format connection direction
      if connection.direction is None:
        connection.direction = ''

      # Set the details for the connection
      connection_details = f'{connection.binary}{connection.direction}'
      if connection_details != '':
        connection_details = f'({connection_details})'

      # Set the string for the connection
      connection_string = f'{node.name}{connection_details}->{connection.node_name}\n'
      data.connections_string = data.connections_string + connection_string

  return data


def save_string_to_file(
  string: str,
  directory_path: str,
  file_name: str,
) -> bool:
  print(directory_path, file_name)
  file_path = path.join(directory_path, file_name) 
  with open(file_path, 'w+') as file:
    file.write(string)
  return True


def main(data: Data) -> Data:
  # Setup
  data = setup_data(data=data)
  # set_engine(engine=data.engine)
  # Get nodes and connections string
  data = setup_nodes_string(data=data)
  data = setup_connections_string(data=data)
  # Format nodes and connections
  # Create a .js file with the formatting
  # modify the nodes and connections string
  # Combine the strings
  data.string = f'{data.nodes_string}\n\n{data.connections_string}'
  # Save string to file
  save_string_to_file(
    string=data.string, 
    directory_path=data.directory_path,
    file_name=data.file_name,
  )

  return data.string
  return True


def example() -> None:
  import yaml


  data = '''
    flowchart:
      nodes: 
      - name: start
        _type: start
        text: start a pyflow test
        url: https://url.com
        connections:
        - node_name: operation
      - name: operation
        _type: operation
        text: do something
        connections:
        - node_name: condition
      - name: condition
        _type: condition
        text: Yes or No?
        connections:
        - node_name: input_output
          _type: 'yes'
        - node_name: subroutine
          _type: 'no'
      - name: input_output
        _type: inputoutput
        input: output
        output: something...
        connections:
        - node_name: end
      - name: subroutine
        _type: subroutine
        text: A Subroutine
        connections:
        - node_name: operation
          direction: right
      - name: end
        _type: end
        text: a_pyflow_test
    '''

  data = '''
    description: "http://flowchart.js.org/ example"
    file_name: flowchart.txt
    nodes: 
    - name: st0
      _type: start
      text: start a_pyflow_test
      url: https://url.com
      connections:
      - node_name: op1
    - name: op1
      _type: operation
      text: do something
      connections:
      - node_name: cond2
    - name: cond2
      _type: condition
      text: Yes or No?
      connections:
      - node_name: io3
        binary: 'yes'
      - node_name: sub4
        binary: 'no'
    - name: io3
      _type: inputoutput
      text: 'output: something...'
      connections:
      - node_name: e5
    - name: sub4
      _type: subroutine
      text: A Subroutine
      connections:
      - node_name: op1
        direction: right
    - name: e5
      _type: end
      text: end a_pyflow_test
    '''
  
  data = yaml.safe_load(data)
  data['directory_path'] = __file__.replace('app.py', 'data')
  data = main(data=data)
  
  # data = yaml.dump(data, indent=2)
  print(data)


if __name__ == '__main__':
  example()


# import requests


# url = 'https://flowchart.js.org/'

# response = requests.get(url)
# print(response.content)
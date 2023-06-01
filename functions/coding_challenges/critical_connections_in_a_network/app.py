#!/usr/bin/env python3

import dataclasses as dc
from copy import deepcopy
from typing import List, Dict
from fastapi import Request

from shared.format_main_arguments import app as format_main_arguments


@dc.dataclass
class Edge:
  values: List[List[int]] | None = None
  excludes: List[int] | None = None
  nodes: List[int] | None = None
  connections: List[List[int]] | None = None


@dc.dataclass
class Body:
  n: int = 0
  connections: List[int] | None = None


@dc.dataclass
class Data:
  body: Body | None = None
  edges: List[List[int]] | List[Edge] | None = None
  output: List[List[int]] | None = None


async def create_edge_objects(data: Data) -> Data:
  store = [Edge(
    values=data.body.connections,
    excludes=[],
  )]
  for i in range(data.body.n):
    edges_copy = deepcopy(data.body.connections)
    edge_object = Edge(
      values=edges_copy,
      excludes=edges_copy[i],
    )
    del edge_object.values[i]
    store.append(edge_object)
  data.edges = store
  return data


async def get_direct_connections_by_nodes(
  edges: List[int],
) -> Dict[int, List[int]]:
  store = {}
  for edge in edges:
    for node in edge:
      if node in store:
        continue
      store[node] = []
    a, b = edge
    store[a].append(b)
    store[b].append(a)
  return store


async def set_indirect_connections_by_nodes(
  connections_by_nodes: Dict[int, List[int]],
  reverse: bool = True,
) -> Dict[int, List[int]]:
  keys = list(connections_by_nodes.keys())
  keys.sort(reverse=reverse)
  for key in keys:
    values = connections_by_nodes[key]
    for value in values:
      indirect_connections = connections_by_nodes[value]
      for node in indirect_connections:
        if node in connections_by_nodes[key]:
          continue
        connections_by_nodes[key].append(node)
  return connections_by_nodes


async def get_unique_connections(
  connections_by_nodes: Dict[int, List[List[int]]],
) -> List[List[int]]:
  store = []
  connections = list(connections_by_nodes.values())
  for connection in connections:
    connection.sort()
    if connection in store:
      continue
    store.append(connection)
  return store


async def get_connections_and_nodes(edges: List[Edge]) -> List[Edge]:
  for edge in edges:
    connections_by_nodes = await get_direct_connections_by_nodes(
      edges=edge.values)
    connections_by_nodes = await set_indirect_connections_by_nodes(
      connections_by_nodes=connections_by_nodes)
    edge.connections = await get_unique_connections(
      connections_by_nodes=connections_by_nodes)
    edge.nodes = list(connections_by_nodes.keys())
    edge.nodes.sort()
  return edges


async def get_critical_edges(edges: List[Edge]) -> List[List[int]]:
  edges_range = range(1, len(edges))
  critical_edges = []
  for i in edges_range:
    # Should have the same number of nodes
    if edges[0].nodes != edges[i].nodes:
      critical_edges.append(edges[i].excludes)
      continue
    # Should have the same number of unique connections
    if len(edges[i].connections) != len(edges[0].connections):
      critical_edges.append(edges[i].excludes)
      continue
    # Should be a subset that has the same elements of one of
    # the original connections
    for connection_wo_edge in edges[i].connections:
      connection_wo_edge.sort()
      critical = False
      for connection in edges[0].connections:
        connection.sort()
        if connection != connection_wo_edge:
          critical = True
          continue
        if connection == connection_wo_edge:
          critical = False
          break

      if critical is True:
        critical_edges.append(edges[i].excludes)

  return critical_edges


async def get_response(data: Data) -> dict:
  critical_connections = [f'{x[0]}.{x[1]}' for x in data.output]
  return {'critical_connections': critical_connections}


# pylint: disable=unused-argument
async def main(
  request: Request | None = None,
  n: int = 0,
  connections: List[int] | None = None,
) -> dict:
  data = await format_main_arguments.main(
    _locals=locals(),
    data_classes={'body': Body},
    main_data_class=Data,
  )
  request = None
  data = await create_edge_objects(data=data)
  edges = await get_connections_and_nodes(edges=data.edges)
  data.output = await get_critical_edges(edges=edges)
  data = await get_response(data=data)
  return data

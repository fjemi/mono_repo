import networkx as nx
from networkx import Graph, DiGraph, from_pandas_edgelist, draw, spring_layout
from pandas import DataFrame, Timestamp
from typing import Optional, Dict, Any, List, Union
from matplotlib.pyplot import figure
from dataclasses import dataclass, asdict, field, fields
from box import Box
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
# Internal Packages
from assets import (
    AssetProps,
    SolarProps,
    StorageProps,
    InverterProps,
    PointOfInterconnectionProps,
    ConverterProps, 
    EdgeProps, )


ABREVIATION_MAP = Box({
    'solar': 'S',
    'storage': 'B',
    'point_of_interconnection': 'POI',
    'POI': 'POI',
})


COLOR_MAP = {
    'solar': 'green',
    'storage': 'blue',
    'point_of_interconnection': 'yellow',
}

def create_graph(
    df: DataFrame = None,
    dict_data: Dict = None,
    color_map: Dict = COLOR_MAP,
) -> Optional[Graph]:
    '''
    Creates a multidirectional networkx graph of a sites assets. Assets 
    represent the nodes of the graph, and edges represent connections between
    nodes or the direction that energy/power flows

    Parameters:
    - df: DataFrame = A pandas dataframe containing asset data
    - dict_data: Dict = A dictionary containing asset data
    
    Returns: Optional[Graph]
    '''

    if df is None and dict_data is None:
        # Log no data error
        return

    # Use dictionary data if passed to function
    if dict_data:
        df = DataFrame.from_dict(dict_data)

    # Check that the dataframe has the necessary columns for adding edges
    columns = [
        'station_id',
        'asset_id',
        'asset_type',
    ]
    for column in columns:
        if column not in df.columns:
            # Log error
            return

    # Check for uniquness of assets
    asset_df = df[columns].drop_duplicates()
    if len(asset_df) != len(df):
        # Log df doesn't contain a unique list of assets
        return

    # Store edges data
    df['edges'] = [[] for x in range(len(df))]
    # Store node color data
    df['node_color'] = [[] for x in range(len(df))]
    
    for i in range(len(df)):
        # Add edge connecting Solar and Storage assets to POI
        if df.iloc[i]['asset_type'].lower() in ['solar', 'storage']:
            df.iloc[i]['edges'].append(EdgeProps(
                node_1=df.iloc[i]['asset_id'],
                node_2=df.iloc[i]['poi_id'],
            ))

        # # Add edge connecting Solar and Storage assets to Inverters
        # if df.iloc[i]['asset_type'].lower() in ['solar', 'storage']:
        #     df.iloc[i]['edges'].append(EdgeProps(
        #         node_1=df.iloc[i]['asset_id'],
        #         node_2=df.iloc[i]['inverter_id'],
        #     ))

        # # Add edge connecting Inverter to POI
        # if df.iloc[i]['asset_type'].lower()  == 'inverter':
        #     df.iloc[i]['edges'].append(EdgeProps(
        #         node_1=df.iloc[i]['inverter_id'],
        #         node_2=df.iloc[i]['poi_id'],
        #     ))

        # Add edge connecting Solar to Storage
        storage_ids = df[df['asset_type'] == 'storage']['asset_id'].tolist()
        if df.iloc[i]['asset_type'].lower() == 'solar':
            # Set Storage assets name
            storage_id = df.iloc[i]['asset_id'].replace('solar', 'storage')
            
            # Skip if Storage assets name is not valid
            if storage_id not in storage_ids:
                continue
            # Add edge connecting Solar and Storage
            edge = EdgeProps(
                node_1=df.iloc[i]['asset_id'],
                node_2=storage_id,
            )
            df.iloc[i]['edges'].append(edge)

    # Create a multidriectional graph
    # graph = DiGraph()
    graph = Graph()
    
    for i in range(len(df)):
        # Add assets as nodes to graph
        graph.add_node(df.iloc[i]['asset_id'], props=df.iloc[i]['asset_props'])
        df.iloc[i]['node_color'] = color_map[df.iloc[i]['asset_type']]

    # asset_wo_poi_df = df[df['asset_type'] != 'point_of_interconnection']    
    for i in range(len(df)):    
        # Add edges to graph
        for edge in df.iloc[i]['edges']:
        # for edge in asset_wo_poi_df.iloc[i]['edges']:
            graph.add_edge(edge.node_1, edge.node_2, props=edge.props)
    
    # Relabel nodes and edges using abbreviations
    mapping = {}
    for node in graph.nodes:
        asset = node.split('_')[0]
        abbreviation = ABREVIATION_MAP[asset]
        node_name = node.replace(asset, abbreviation)
        mapping[node] = node_name
    graph = nx.relabel_nodes(graph, mapping)
    
    return Box({'graph': graph, 'node_color': df['node_color'].tolist()})


def main():
    from create_graph_data import create_graph_data
    from save_graph_image_to_file import save_graph_image_to_file


    # Create dummy data: 60 solar and 20 storage assets
    df = create_dummy_data()
    print(df)
    # Create the graph
    data = create_graph(df=df)
    print(data.graph)
    print('nodes', data.graph.nodes)
    print('edges', data.graph.edges)


if __name__ == '__main__':
    main()

# External Packages
import networkx as nx
from networkx import Graph, DiGraph
from pandas import DataFrame, Timestamp
from typing import Optional, Dict, Any, List, Union
from matplotlib.pyplot import figure
from dataclasses import dataclass, asdict, field, fields
from box import Box
import numpy as np
# Internal Packages
from assets import EdgeProps


ABREVIATION_MAP = Box({
    'solar': 'S',
    'storage': 'B',
    'point_of_interconnection': 'POI',
    'POI': 'POI',
    'inverter': 'I',
    'converter': 'C',
})

COLOR_MAP = {
    'solar': 'green',
    'storage': 'blue',
    'point_of_interconnection': 'yellow',
    'inverter': 'pink',
    'converter': 'orange',
}

def create_dc_coupled_graph(
    df: DataFrame = None,
    dict_data: Dict = None,
    color_map: Dict = COLOR_MAP,
) -> Optional[Dict]:
    '''
    Creates a multidirectional networkx graph of a sites assets. Assets 
    represent the nodes of the graph, and edges represent connections between
    nodes or the direction that energy/power flows

    Parameters:
    - df: DataFrame = A pandas dataframe containing asset data
    - dict_data: Dict = A dictionary containing asset data
    - 
    
    Returns: Optional[Dict]
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
        # Add edge connecting Inverter to POI
        if df.iloc[i]['asset_type'].lower()  == 'inverter':
            df.iloc[i]['edges'].append(EdgeProps(
                node_1=df.iloc[i]['inverter_id'],
                node_2=df.iloc[i]['poi_id'],
            ))

        # Add edge connecting Storage and Solar assets to Converters
        storage_ids = df[df['asset_type'] == 'storage']['asset_id'].tolist()
        if df.iloc[i]['asset_type'].lower() == 'converter':
            # Set Storage assets name
            storage_id = df.iloc[i]['asset_id'].replace('converter', 'storage')
            solar_id = df.iloc[i]['asset_id'].replace('converter', 'solar')
            
            # Skip if Storage assets name is not valid
            if storage_id not in storage_ids:
                continue
            # Add edge connecting Converter and Storage
            edge = EdgeProps(
                node_1=df.iloc[i]['asset_id'],
                node_2=storage_id, )
            df.iloc[i]['edges'].append(edge)

            # Add edge connecting Solar and Converter
            edge = EdgeProps(
                node_2=df.iloc[i]['asset_id'],
                node_1=solar_id, )
            df.iloc[i]['edges'].append(edge)

        # Add edge connecting Solar and Storage assets to Inverters
        if df.iloc[i]['asset_type'].lower() in ['solar', 'storage']:
            df.iloc[i]['edges'].append(EdgeProps(
                node_1=df.iloc[i]['asset_id'],
                node_2=df.iloc[i]['inverter_id'],
            ))

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
    from create_dc_coupled_data import create_dc_coupled_data

    # Create dummy data
    df = create_dc_coupled_data(solar_count=60, storage_count=40)

    # Create the graph
    data = create_dc_coupled_graph(df=df)
    print(data.graph)
    print('nodes', data.graph.nodes)
    print('edges', data.graph.edges)


if __name__ == '__main__':
    main()

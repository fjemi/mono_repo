from typing import Dict, Union, List
from networkx import Graph, DiGraph, draw, nx_agraph
import matplotlib
from matplotlib import pyplot as plt
from os import getenv


# Node color
COLOR_MAP = {
    'solar': 'green',
    'storage': 'blue',
    'point_of_interconnection': 'yellow',
    'inverter': 'pink',
    'converter': 'orange',
}
# Save files here
IMAGE_PATH = getenv('ROOT_PATH') + '/ignore/'


# @exception_handler
def save_graph_image_to_file(
    filename: str = 'graph.png',
    graph: Union[Graph, DiGraph] = None,
    image_path: str = IMAGE_PATH,
    node_color: List['str'] = None,
    color_map: Dict = COLOR_MAP,
    image_height: int = 30,
    image_width: int = 30,
    node_size: int = 1400,
) -> None:
    '''

    Parameters:
    - data: 

    Returns: None
    '''
    figure = plt.figure(figsize=(image_height, image_width))
    # Setup the legend
    ax = figure.add_subplot(1,1,1)
    for key in color_map.keys():
        ax.plot(
            [0],
            [0],
            color=color_map[key],
            label=key,
        )
    # Use Graphviz to plot Graph
    pos = nx_agraph.graphviz_layout(graph)
    draw(
        graph,
        pos=pos,
        with_labels=True,
        node_size=node_size,
        node_color=node_color,
        ax=ax, ) 
    # Add the legend to the plot
    plt.legend()
    # Save the plot to file
    path = image_path + filename
    figure.savefig(path)
    return True


if __name__ == '__main__':
    from create_dc_coupled_data import create_dc_coupled_data
    from create_dc_coupled_graph import create_dc_coupled_graph


    df = create_dc_coupled_data()
    graph = create_dc_coupled_graph(df=df)
    save_graph_image_to_file(
        filename='graph_dc_coupled.png',
        graph=graph.graph,
        node_color=graph.node_color, )
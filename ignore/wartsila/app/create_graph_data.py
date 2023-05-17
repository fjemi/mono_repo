# External Packages
from pandas import DataFrame, Timestamp
from box import Box
from typing import Optional
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



def create_graph_data(
    solar_assets_count: int = 60,
    storage_assets_count: int = 40,
) -> Optional[DataFrame]:
    '''
    Creates a dataframe containing dummy data that can be used for creating a 
    networkx graph

    Paramters:
    - solar_assets_count: int = The number of solar assets to create
    - storage_assets_count: int = The number of solar assets to create

    Returns: DataFrame
    '''

    # Store assets
    store = []

    # Create a POI asset and add to store
    poi_data = AssetProps(
        poi_id='POI_0',
        station_id=None,
        asset_id='POI_0',
        inverter_id=None,
        asset_type='point_of_interconnection',
        asset_props=PointOfInterconnectionProps(), # Add all props together 
    )
    store.append(poi_data)

    # Add solar units
    for i in range(solar_assets_count):
        solar_data = AssetProps(
            poi_id='POI_0',
            station_id=f'station_{i}',
            inverter_id=f'inverter_{i}',
            asset_id=f'solar_{i}',
            asset_type='solar',
            asset_props=SolarProps(), # Add all props together 
        )
        store.append(solar_data)
    
    # Add storage units
    for i in range(storage_assets_count):        
        storage_data = AssetProps(
            poi_id='POI_0',
            station_id=f'station_{i}',
            inverter_id=f'inverter_{i}',
            asset_id=f'storage_{i}',
            asset_type='storage',
            asset_props=StorageProps(),
        )
        store.append(storage_data)
    
    # Load data into datframe
    df = DataFrame.from_dict(store)
    return df


if __name__ == '__main__':
    df = create_graph_data()
    print(df)
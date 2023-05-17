# External Packages
from pandas import DataFrame
from typing import Optional
from random import uniform
# Internal Packages
from assets import (
    AssetProps,
    SolarProps,
    StorageProps,
    InverterProps,
    PointOfInterconnectionProps,
    ConverterProps, )


def create_dc_coupled_data(
    solar_count: int = 60,
    storage_count: int = 40,
    poi_count: int = 1,
) -> Optional[DataFrame]:
    '''
    Creates a dataframe containing dummy data that can be used for creating a 
    networkx graph

    Paramters:
    - solar_count: The number of solar assets to create
    - storage_count: The number of solar assets to create
    - poi_count: The number of points of interconnection to create

    Returns: DataFrame
    '''

    # Store assets
    store = []

    # Add POIs
    for i in range(poi_count):
        poi_data = AssetProps(
            poi_id='POI_0',
            station_id=None,
            asset_id='POI_0',
            inverter_id=None,
            asset_type='point_of_interconnection',
            asset_props=PointOfInterconnectionProps(), # Add all props together 
        )
        store.append(poi_data)

    # Add inveters
    inverter_count = solar_count
    for i in range(inverter_count):
        # random_poi = int(uniform(0, poi_count - 1))
        inverter_data = AssetProps(
            # poi_id=f'POI_{random_poi}',
            poi_id=f'POI_{0}',
            station_id=f'station_{i}',
            inverter_id=f'inverter_{i}',
            asset_id=f'inverter_{i}',
            asset_type='inverter',
            asset_props=InverterProps(), # Add all props together 
        )
        store.append(inverter_data)

    # Add converters
    converter_count = storage_count
    for i in range(converter_count):
        converter_data = AssetProps(
            poi_id='POI_0',
            station_id=f'station_{i}',
            asset_id=f'converter_{i}',
            asset_type='converter',
            asset_props=ConverterProps(), # Add all props together 
        )
        store.append(converter_data)

    # Add solar units
    for i in range(solar_count):
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
    for i in range(storage_count):        
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
    df = create_dc_coupled_data()
    print(df)
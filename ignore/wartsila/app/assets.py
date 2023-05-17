from typing import List, Dict
from dataclasses import dataclass, field
from pandas import Timestamp, Series

@dataclass
class AssetProps:
    '''
    Stores asset properties

    Attributes
    - station_id: str = The ID of the station the asset is assoicated with
    - asset_type: str = The type of asset (Solar, Storage, etc)
    - asset_id: str = The ID or name of the asset
    - prop_name: str = The name of a property for the asset
    - prop_value: Any = The value of the asset's property
    '''
    poi_id: str = None
    station_id: str = None
    inverter_id: str = None
    asset_id: str = None
    asset_type: str = None
    asset_props: Dict = None
    # prop_name: str = None
    # prop_value: Any = None


@dataclass
class StorageProps:
    '''Properties for Batteries'''
    rated_energy: float = 0
    rated_power_charge: float = 0
    rated_power_discharge: float = 0
    max_soc: float = 0
    min_soc: float = 0
    efficiency: float = 0
    mip: bool = False
    cycling_cost: float = 0
    timestamps: List[Timestamp] = field(default_factory=lambda: [])


@dataclass 
class SolarProps:
    '''Properties for PV'''
    inverter_max_power: float = 0
    timestamps: List[Timestamp] = field(default_factory=lambda: [])


@dataclass
class InverterProps:
    '''Properties for Inverters'''
    max_power: float = 0


@dataclass
class ConverterProps:
    '''Properties for Converters'''
    pass


@dataclass
class PointOfInterconnectionProps:
    '''Properties for Converter assets'''
    pass


@dataclass
class EdgeProps:
    '''
    Properties for a networkxx edge between two nodes
    
    Attributes:
    - right: str = The second node
    - left: str = The first node
    - props: Dict = properties associated with the edge

    Links:
    - https://stackoverflow.com/questions/46575740/are-networkx-edges-multi-directional
    '''
    node_1: str
    node_2: str
    props: Dict = field(default_factory=lambda: {})
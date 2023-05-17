
# Standard
from datetime import datetime
from dataclasses import dataclass
from typing import Union
from os.path import dirname
import json
# External
from box import Box
import pandas as pd
import numpy as np


DATA_DIR = f'{dirname(__file__)}/data'


@dataclass
class Data:
    pass


def time_it(func):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    def wrapper(data: Union[Data, dict]) -> Union[int, float]:
        start = datetime.utcnow()
        loop = func(data)
        execution_time = (datetime.utcnow() - start).total_seconds()
        return {'loop': func.__name__, 'execution_time': execution_time}
    return wrapper


# @time_it
def add(data: Union[Data, dict]) -> Union[float, int]:
    if isinstance(data, dict):
        data = Box(data)
    return data.a + data.b


# @time_it
def multiply(data: Union[Data, dict]) -> Union[float, int]:
    if isinstance(data, dict):
        data = Box(data)
    return data.a * data.b


def create_df(data: Union[Data, dict]) -> Data:
    '''Create or load pickled dataframe after initilization'''
    pickle_path = f'{DATA_DIR}/df_{data.n}.pkl'
    columns = list('ab')
    try:            
        # Load pickled df if exists
        data.df = pd.read_pickle(pickle_path)
    except Exception as e:
        # Create dataframe with random numbers
        data.df = pd.DataFrame(
            np.random.randint(0, 1000, size=(data.n, len(columns))),
            columns=columns, )
        # Pickle the dataframe
        data.df.to_pickle(pickle_path)
    data.dict = data.df.to_dict(orient='records')
    return data


@time_it
def standard_for_loop_df(data: Union[Data, dict]):
    for i in range(len(data.df)):
        add(data.df.iloc[i])


@time_it
def standard_for_loop_df_index(data: Union[Data, dict]):
    for i in data.df.index:
        add(data.df.loc[i])


@time_it
def standard_for_loop_dict(data: Union[Data, dict]):
    for i in range(len(data.df)):
        add(data.dict[i])


@time_it
def pandas_apply(data: Union[Data, dict]):
    data.df.apply(lambda x: add({'a': x['a'], 'b': x['b']}), axis=1)


@time_it
def pandas_only(data: Union[Data, dict]):
    data.df['a'] + data.df['b']


@time_it
def standard_for_loop_dict(data: Union[Data, dict]):
    for i in range(len(data.df)):
        add(data.dict[i])


if __name__ == '__main__':
    data = Box(a=1, b=2)
    #print(add(data))
    #print(multiply(data))

    data = Box(n=1000000)
    data = create_df(data)
    #print(data)

    store = [
        standard_for_loop_df_index(data),
        standard_for_loop_df(data),
        standard_for_loop_dict(data),
        pandas_apply(data),
        pandas_only(data),
    ]
    print(json.dumps(store), indent=2)
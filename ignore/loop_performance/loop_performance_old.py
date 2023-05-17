# data analysis/wrangling
#import modin.pandas as pd
import pandas as pd
import numpy as np
# import perfplot
# data modeling
import attr
from typing import Dict, List
# loop progress
# from tqdm import trange, tqdm
import itertools as it
# date
from datetime import datetime
# from timeme import timeme
# Web/JSON
import json
# decorators
from functools import wraps


def add(a, b):
    return a + b


def multiply(a, b):
    return a * b


def time_it(func):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    def wrapper(data):
        start = datetime.utcnow()
        loop = func(data)
        execution_time = (datetime.utcnow() - start).total_seconds()
        result = Result(data.size, loop, execution_time)
        return result
    return wrapper



@attr.s
class Result:
    size: int = attr.ib()
    loop_type: str = attr.ib()
    execution_time: int = attr.ib()


@attr.s
class Loop:
    size: int = attr.ib(default=None, repr=False)
    df: pd.DataFrame = attr.ib(default=None, repr=False)
    result: List[Result] = attr.ib(default=[], repr=False)
    
    
    def _timeit(func):
        '''Decorator hidden from the class methods'''                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
        def wrapper(self, *args, **kwargs):
            start = datetime.utcnow()
            loop = func(self, *args, **kwargs)
            execution_time = (datetime.utcnow() - start).total_seconds()
            result = Result(self.size, loop, execution_time)
            result = attr.asdict(result)
            self.result.append(result)
        return wrapper
        
        
    def set_df(self, size):
        '''Create or load pickled dataframe after initilization'''
        try:            
            # Load pickled df if exists
            df = pd.read_pickle('df{}.pkl'.format(size))
        
        except Exception as e:
            # Create dataframe with random numbers
            df = pd.DataFrame(np.random.randint(0, 1000, size=(size, 2)), columns=list('ab'))
            # Pickle pandas object
            df.to_pickle('df.pkl')
            
        finally:
            self.df = df
            self.size = size
            
            
    @_timeit        
    def use_list_comprehension(self, loop):
        [add(a, b) for a, b in zip(self.df.a, self.df.b)]
        return loop
        
    
    @_timeit 
    def use_for(self, loop):
        for i in range(len(self.df)):
            add(self.df.a.iloc[i], self.df.a.iloc[i])
        return loop
        
    
    @_timeit     
    def use_while(self, loop):
        i = len(self.df) - 1
        while i != 0:
            add(self.df.a.iloc[i], self.df.a.iloc[i])
            i = i - 1
        return loop
        
    
    @_timeit     
    def use_zip(self, loop):
        for (a, b) in zip(self.df.a, self.df.b):
            add(a, b)
        return loop
        
    
    @_timeit 
    def use_apply(self, loop):   
        self.df.apply(lambda x: add(x['a'], x['b']), axis=1)
        return loop
        
    
    @_timeit 
    def use_map(self, loop):
        map(add, (add(self.df['a'].values, self.df['b']).values))
        return loop
    
    
    @_timeit 
    def use_filter(self, loop):
        filter(multiply, (add(self.df['a'].values, self.df['b']).values))
        return loop
        
    
    @_timeit 
    def use_pandas(self, loop):
        add(self.df['a'], self.df['b'])
        return loop
        
    
    @_timeit 
    def use_numpy(self, loop):
        add(self.df.b.values, self.df.a.values)
        return loop
        
    
    @_timeit     
    def use_iterrows(self, loop):
        for index, row in self.df.iterrows():
            add(row.a, row.b)
        return loop

    
    @_timeit 
    def use_itertuples(self, loop):
        for row in self.df.itertuples():
            add(row.a, row.b)
        return loop
    
    
    @_timeit
    def use_itertools(self, loop):
        limit = 0
        for row in it.chain(self.df.values):
            limit += 1
            if limit == len(self.df):
                break
            add(row[0], row[1])
        return loop
        
    
    @_timeit 
    def use_iter_while(self, loop):
        iterator = iter(self.df.values)
        stop_loop = False
        
        while not stop_loop:
            try: 
                i = next(iterator)
                add(i[0], i[1])

            except:
                stop_loop = True
        return loop
    
    
# Execute when script is run as main module       
if __name__ == '__main__':
    sizes = [10000000]
    iterators = ['for', 'list_comprehension', 'while', 'zip', 'apply', 'pandas', 'numpy', 'map', 'filter', 'itertools', 'iterrows', 'itertuples', 'iter_while']

    # Initialize the Loop object
    l = Loop()
    
    for size in sizes:
        l.set_df(size)
        
        for iterator in iterators:
            # Evaluate Loop functions
            loop = 'l.use_{}("{}")'.format(iterator, iterator)
            eval(loop)
    
    # Save results to JSON
    with open('data.json', 'w') as file:
        json.dump(l.result, file, indent=2)
    print(json.dumps(l.result, indent=2))
    
    
    
'''
things to implement
cython, c++, java, pyjnius, fortran for loop, numba
refactor to attrs
api, js frontend
'''
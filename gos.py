"""
The Global Open Simulator.
"""

import numpy as np
import pandas as pd
import gc
from multiprocessing import Pool, cpu_count
from functools import partial

class Globe:
    def __init__(self, df, threads=cpu_count() - 1, splits=1):
        self.df = df
        self.threads = threads
        self.splits = splits
    
    def max_value(self, attribute):
        """
        Returns the maximum value for an attribute.
        """
        return self.df[attribute].max()

    def _gen_agents(self, array):
        return pd.concat([self.generator(self.df, country, len(population)) for country, population in array.groupby(array)])

    def create_agents(self, generator):
        self.generator = generator
        country_array = pd.concat([pd.Series([c] * k["Population"]) for c, k in self.df.iterrows()])
        country_array.index = range(len(country_array))
        # Garbage collect before creating new processes.
        gc.collect()
        with Pool(self.threads) as p:
            self.agents = pd.concat(p.imap_unordered(self._gen_agents, np.array_split(country_array, self.threads * self.splits)))
            p.close()
            p.join()

    def run(self, function, **kwargs):
        # Garbage collect before creating new processes.
        gc.collect()
        with Pool(self.threads) as p:
            self.agents = pd.concat(p.imap_unordered(partial(function, **kwargs),
                                                     np.array_split(self.agents,
                                                                    self.threads * self.splits)))
            p.close()
            p.join()
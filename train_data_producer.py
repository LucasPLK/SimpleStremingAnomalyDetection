import pandas as pd
import time
import numpy as np

x = 1_000


pd.DataFrame.from_dict({
            'time': None,
            'sin': None,
            'sawtooth': None,
            'random': None,
            'sqrt': None,
            'equation': None
        }, orient='index').T.to_csv('train2.csv', index=False)



while(x>0):
    for i in np.arange(0, 2*np.pi, 0.2):
        rand = np.random.rand()

        body = {
            'time': x+i,
            'sin': np.sin(i)*np.random.rand()/10,
            'sawtooth': i,
            'random': rand,
            'sqrt': np.sqrt(i),
            'equation': np.sin(i)*2+i+rand+np.sqrt(i)*3
        }

        pd.DataFrame.from_dict(body, orient='index').T.to_csv('train2.csv', mode='a', header=False, index=False)
    x = x-1
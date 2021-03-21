__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import time
import pandas as pd


def MRFI(df, timeperiod: int = 14):
    """Calculates Money Relative Flow Index."""
    previous_mrfi_basis = 0
    previous_inverse_mrfi = 0
    previous_mrfi = 0

    data = {
        'time': [],
        'mrfi': [],
        'mrfi_inverse': [],
        'mrfi_basis': [],
    }

    for i, row in df.iterrows():
        if row['rsi'] == 0:
            mrfi_basis = previous_mrfi_basis
        else:
            mrfi_basis = float(row['mfi'] / row['rsi']) * ((row['rsi'] + row['mfi']) / 2)
            previous_mrfi_basis = mrfi_basis

        if row['mfi'] == 0:
            mrfi_inverse = previous_inverse_mrfi
        else:
            mrfi_inverse = float(row['rsi'] / row['mfi']) * ((row['rsi'] + row['mfi']) / 2)
            previous_inverse_mrfi = mrfi_inverse
        
        if mrfi_basis > float(100):
            mrfi_basis = float(100)
        if mrfi_basis < float(0.01):
            mrfi_basis = float(0)
        if mrfi_inverse > float(100):
            mrfi_inverse = float(100)
        if mrfi_inverse < float(0.01):
            mrfi_inverse = float(0)

        mrfi = float((mrfi_basis + mrfi_inverse) / 2)

        if mrfi > float(100):
            mrfi = float(100)
        if mrfi < float(0.01):
            mrfi = float(0)

        data['time'].append(row['timestamp'])
        data['mrfi'].append(mrfi)
        data['mrfi_inverse'].append(mrfi_inverse)
        data['mrfi_basis'].append(mrfi_basis)

    mrfi_df = pd.DataFrame(data).set_index('time')
    mrfi_df['smrfi'] = mrfi_df.mrfi.rolling(window=timeperiod).mean()
    return mrfi_df
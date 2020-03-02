__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import time
import pandas as pd
from datetime import datetime
from talib import abstract as abstract_ta
from talib import MA_Type
from playground.settings import DATASET_FOLDER

def MRFI(df):
    previous_mrfi = 0
    previous_inverse_mrfi = 0
    previous_avg_mrfi = 0

    data = {
        'mrfi': [],
        'mrfi_inverse': [],
        'mrfi_avg': [],
    }

    start = time.time()

    for i, row in df.iterrows():
        if row['rsi'] == 0:
            mrfi = previous_mrfi
        else:
            mrfi = (row['mfi'] / row['rsi']) * ((row['rsi'] + row['mfi']) / 2)
            previous_mrfi = mrfi

        if row['mfi'] == 0:
            mrfi = previous_inverse_mrfi
        else:
            mrfi_inverse = (row['rsi'] / row['mfi']) * ((row['rsi'] + row['mfi']) / 2)
            previous_inverse_mrfi = mrfi_inverse
        
        mrfi_avg = (mrfi + mrfi_inverse) / 2

        if mrfi > 100:
            mrfi = 100
        if mrfi_inverse > 100:
            mrfi_inverse = 100
        if mrfi_avg > 100:
            mrfi_avg = 100

        data['mrfi'].append(mrfi)
        data['mrfi_inverse'].append(mrfi_inverse)
        data['mrfi_avg'].append(mrfi_avg)

    end = time.time()
    mrfi_df = pd.DataFrame(data)

    df['mrfi'] = mrfi_df['mrfi']
    df['mrfi_avg'] = mrfi_df['mrfi_avg']
    df['mrfi_inverse'] = mrfi_df['mrfi_inverse']

    return df

def process_indicators(df):
        
    # EMA Cross (simple and wrong probably)
    df['ema20_cross'] = (df.ema20 > df.ema50) | (df.ema20 > df.ema100)
    df['ema50_cross'] = (df.ema50 > df.ema100)

    # Bollinger Bands Crossing
    df['touch_upper'] = df.high >= df.upper
    df['touch_lower'] = df.low  <= df.lower
    df['crossing_dn'] = (df.close < df.middle) & (df.open > df.middle)
    df['crossing_up'] = (df.close > df.middle) & (df.open < df.middle)

    # Medivh Relative Flow Index
    df['mrfi_ob'] = df.mrfi_avg > 90
    df['mrfi_os'] = df.mrfi_avg < 30

    return df


class Analyzer:
    @staticmethod
    def analyze(item, df: pd.DataFrame = None):
        
        dataset = Analyzer.add_indicators(df=df)

        dataset_file = DATASET_FOLDER + '{}_{}_analyzed.csv'.format(item['pair'], item['timeframe']).replace(' ', '')

        #print('{} - {} - DATASET \n '.format(item['pair'], item['timeframe']) + str(df))
        dataset.to_csv(dataset_file)

    @staticmethod
    def process_indicators(df: pd.DataFrame = None) -> pd.DataFrame:

        # EMA Cross (simple and wrong probably)
        df['ema20_cross'] = (df.ema20 > df.ema50) | (df.ema20 > df.ema100)
        df['ema50_cross'] = (df.ema50 > df.ema100)

        # Bollinger Bands Crossing
        df['touch_upper'] = df.high >= df.upper
        df['touch_lower'] = df.low  <= df.lower
        df['crossing_dn'] = (df.close < df.middle) & (df.open > df.middle)
        df['crossing_up'] = (df.close > df.middle) & (df.open < df.middle)

        # Medivh Relative Flow Index
        df['mrfi_ob'] = df.mrfi_avg > 90
        df['mrfi_os'] = df.mrfi_avg < 30
        return df

    @staticmethod
    def add_indicators(df: pd.DataFrame = None) -> pd.DataFrame:
        
        cols = ['high', 'low', 'open', 'close', 'volume']
        HLOCV = {key: df[key].values for key in df if key in cols}

        try:
            df['volume'] = df['volumeto']
        except:
            pass

        # Moving Averages
        df['sma'] = abstract_ta.SMA(df, timeperiod=25)
        df['ema20'] = abstract_ta.EMA(df, timeperiod=20)
        df['ema50'] = abstract_ta.EMA(df, timeperiod=50)
        df['ema100'] = abstract_ta.EMA(df, timeperiod=100)

        # Bollinger Bands
        u, m, l = abstract_ta.BBANDS(HLOCV, timeperiod=24, nbdevup=2.5, nbdevdn=2.5, matype=MA_Type.T3)
        df['upper']  = u
        df['middle'] = m
        df['lower']  = l

        # Stochastic
        # uses high, low, close (default)
        slowk, slowd = abstract_ta.STOCH(HLOCV, 5, 3, 0, 3, 0) # uses high, low, close by default
        df['slowk'] = slowk
        df['slowd'] = slowd

        # Relative Strength Index
        rsi = abstract_ta.RSI(df, timeperiod=14)
        df['rsi'] = rsi

        # Money Flow Index
        mfi = abstract_ta.MFI(df, timeperiod=14)
        df['mfi'] = mfi

        # Medivh Relative Flow Index
        mrfi_df = MRFI(df)
        df['mrfi'] = mfi
        return Analyzer.process_indicators(df)
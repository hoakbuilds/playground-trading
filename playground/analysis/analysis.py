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
from playground import settings as s
from playground.analysis.mrfi import MRFI
from playground.util import setup_logger

logger = setup_logger(name=__name__)


class Analyser:
    """
    Basic class that defines and performs asset analysis.
    TODO: Define indicator additions and make these functional instead of static.
    TODO-2: refactor this whole god damn thing please
    """

    def __init__(self, item: dict) -> None:
        """ Initialize. """
        dataset: pd.DataFrame = pd.DataFrame()
        initial_file = s.DATASET_FOLDER + '{}_{}.csv'.format(item.get('pair'), item.get('timeframe')).replace(' ', '')
        final_file = s.DATASET_FOLDER + '{}_{}_analyzed_v1.csv'.format(item.get('pair'), item.get('timeframe')).replace(' ', '')
        try:
            dataset = pd.read_csv(initial_file, nrows=s.MAX_ROWS, error_bad_lines=False).set_index('time')
        except KeyError:
            dataset = pd.read_csv(initial_file, error_bad_lines=False).set_index('time')
        dataset.sort_index(inplace=True, ascending=True)

        if s.ANALYSIS_VERBOSITY:
            logger.info('-------'*20 + str(item))
            logger.info(initial_file)
            logger.info(final_file)
            logger.info('IDF ' + str(dataset))
        
        dataset = self.analyse(item=item, df=dataset)

        if s.ANALYSIS_VERBOSITY:
            logger.info( '{} - {} - DATASET FINAL -\n {} '.format(item['pair'], item['timeframe'], str(dataset)) + '-------'*20)

        dataset.sort_index(inplace=True, ascending=False)
        dataset.to_csv(final_file)

    def analyse(self, item: dict, df: pd.DataFrame) -> pd.DataFrame:
        """ Method that performs needed logic before actually performing analysis. """

        df = self.add_indicators(df=df)

        df = self.process_indicators(df=df)

        return df

    def crossover(
        self, df: pd.DataFrame = None, crossing_col: str = '', crossed_col: str = '', new_col: str = '',
    ) -> pd.DataFrame:
        """Perform crossover logic on passed columns, return the data to the passed new_col."""

        previous_crossing_col = df[crossing_col].shift(1)
        previous_crossed_col = df[crossed_col].shift(1)

        crossing = ((df[crossing_col] > df[crossed_col]) & (previous_crossing_col < previous_crossed_col))
        df.loc[crossing, new_col] = True
        df[new_col].fillna(value='False', inplace=True)

        return df[new_col]

    def process_indicators(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Process the indicators added."""

        # EMA Cross
        df['ema20_50_cross'] = self.crossover(df=df, crossing_col='ema20', crossed_col='ema50', new_col='ema20_50_cross')
        df['ema20_100_cross'] = self.crossover(df=df, crossing_col='ema20', crossed_col='ema100', new_col='ema20_100_cross')
        df['ema50_100_cross'] = self.crossover(df=df, crossing_col='ema50', crossed_col='ema100', new_col='ema50_100_cross')
        df['ema100_200_cross'] = self.crossover(df=df, crossing_col='ema100', crossed_col='ema200', new_col='ema100_200_cross')
        df['ema100_300_cross'] = self.crossover(df=df, crossing_col='ema100', crossed_col='ema300', new_col='ema100_300_cross')

        # EMA Cross-under
        df['ema50_20_cross'] = self.crossover(df=df, crossing_col='ema50', crossed_col='ema20', new_col='ema50_20_cross')
        df['ema100_20_cross'] = self.crossover(df=df, crossing_col='ema100', crossed_col='ema20', new_col='ema100_20_cross')
        df['ema100_50_cross'] = self.crossover(df=df, crossing_col='ema100', crossed_col='ema50', new_col='ema100_50_cross')
        df['ema200_100_cross'] = self.crossover(df=df, crossing_col='ema200', crossed_col='ema100', new_col='ema200_100_cross')
        df['ema300_100_cross'] = self.crossover(df=df, crossing_col='ema300', crossed_col='ema100', new_col='ema300_100_cross')

        # Bollinger Bands Crossing
        df['touch_upper'] = df.high >= df.upper
        df['touch_lower'] = df.low  <= df.lower
        df['crossing_dn'] = (df.close < df.middle) & (df.open > df.middle)
        df['crossing_up'] = (df.close > df.middle) & (df.open < df.middle)

        # Medivh Relative Flow Index
        df['smrfi_ob'] = df.smrfi > 70
        df['smrfi_os'] = df.smrfi < 30
        df['mrfi_ob'] = df.mrfi > 75
        df['mrfi_os'] = df.mrfi < 25
        df['mfi_os'] = df.mrfi < 20
        df['mfi_ob'] = df.mrfi > 80
        df['rsi_os'] = df.mrfi < 30
        df['rsi_ob'] = df.mrfi > 70

        # Stoch Cross SMRFI / MRFI
        df['slow_stoch_crossover_smrfi'] = self.crossover(df=df, crossing_col='slow_stoch', crossed_col='smrfi', new_col='slow_stoch_crossover_smrfi')
        df['slow_stoch_crossover_mrfi'] = self.crossover(df=df, crossing_col='slow_stoch', crossed_col='mrfi', new_col='slow_stoch_crossover_mrfi')
        df['slow_stoch14_crossover_smrfi'] = self.crossover(df=df, crossing_col='slow_stoch_sma14', crossed_col='smrfi', new_col='slow_stoch14_crossover_smrfi')
        df['slow_stoch14_crossover_mrfi'] = self.crossover(df=df, crossing_col='slow_stoch_sma14', crossed_col='mrfi', new_col='slow_stoch14_crossover_mrfi')

        df['slow_stoch_crossunder_smrfi'] = self.crossover(df=df, crossing_col='smrfi', crossed_col='slow_stoch', new_col='slow_stoch_crossunder_smrfi')
        df['slow_stoch_crossunder_mrfi'] = self.crossover(df=df, crossing_col='mrfi', crossed_col='slow_stoch', new_col='slow_stoch_crossunder_mrfi')
        df['slow_stoch14_crossunder_smrfi'] = self.crossover(df=df, crossing_col='smrfi', crossed_col='slow_stoch_sma14', new_col='slow_stoch14_crossunder_smrfi')
        df['slow_stoch14_crossunder_mrfi'] = self.crossover(df=df, crossing_col='mrfi', crossed_col='slow_stoch_sma14', new_col='slow_stoch14_crossunder_mrfi')

        return df

    def add_indicators(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Add indicators."""

        cols = ['high', 'low', 'open', 'close', 'volume']
        HLOCV = {key: df[key].values for key in df if key in cols}

        try:
            df['volume'] = df['volumefrom'] * df['volumeto']
        except:
            pass

        # Moving Averages
        df['sma'] = abstract_ta.SMA(df, timeperiod=25)
        df['ema20'] = abstract_ta.EMA(df, timeperiod=20)
        df['ema50'] = abstract_ta.EMA(df, timeperiod=50)
        df['ema100'] = abstract_ta.EMA(df, timeperiod=100)
        df['ema200'] = abstract_ta.EMA(df, timeperiod=200)
        df['ema300'] = abstract_ta.EMA(df, timeperiod=300)

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
        df['slow_stoch'] = (slowk + slowd)/2
        df['slow_stoch_sma14'] = df.slow_stoch.rolling(window=14).mean()

        # Relative Strength Index
        rsi = abstract_ta.RSI(df, timeperiod=14)
        df['rsi'] = rsi

        # Money Flow Index
        mfi = abstract_ta.MFI(df, timeperiod=14)
        df['mfi'] = mfi

        # Medivh Relative Flow Index
        mrfi_df = MRFI(df)
        df['mrfi'] = mrfi_df['mrfi'].astype(float)
        df['smrfi'] = mrfi_df['smrfi'].astype(float)
        df['mrfi_basis'] = mrfi_df['mrfi_basis'].astype(float)
        df['mrfi_inverse'] = mrfi_df['mrfi_inverse'].astype(float)

        return df
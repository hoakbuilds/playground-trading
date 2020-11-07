__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import pandas as pd
from queue import Queue
from logging import Logger
from talib import abstract as abstract_ta
from talib import MA_Type
from playground import settings as s
from playground.analysis.mrfi import MRFI
from playground.util import setup_logger



class Analysis:
    """
    Base class that defines and performs asset analysis.
    """

    logger: Logger = None

    dataset: pd.DataFrame = None
    df: pd.DataFrame = None

    initial_file: str = None
    final_file: str = None
    
    read_queue: Queue = None

    def __init__(self, item: dict = None) -> None:
        """ Initialize. """

        self.logger = setup_logger(name=__name__)

        self.read_queue = Queue()

        if item is not None:
            self.run(item=item)

    def run(self, item: dict = None) -> None:
        """
        Run it.
        """
        self.prepare_dataset(item=item)
        self.analyse(df=self.dataset)
        self.save_dataset(item=item)

    def get_read_queue(self) -> Queue:
        """
        Get the reading Queue.
        """
        return self.read_queue

    def prepare_dataset(self, item: dict) -> None:
        """
        Prepares the Analyser and Dataset for analysis.
        """
        self.initial_file = s.DATASET_FOLDER + '{}_{}.csv'.format(item.get('pair'), item.get('timeframe')).replace(' ', '')
        self.final_file = s.DATASET_FOLDER + '{}_{}_analyzed_v1.csv'.format(item.get('pair'), item.get('timeframe')).replace(' ', '')

        try:
            self.dataset = pd.read_csv(self.initial_file, nrows=s.MAX_ROWS, error_bad_lines=False).set_index('time')
        except KeyError:
            self.dataset = pd.read_csv(self.initial_file, error_bad_lines=False).set_index('time')
        self.dataset.sort_index(inplace=True, ascending=True)

        if s.ANALYSIS_VERBOSITY:
            self.logger.info('-------'*20 + str(item))
            self.logger.info(self.initial_file)
            self.logger.info(self.final_file)
            #self.logger.info('IDF ' + str(dataset))

    def save_dataset(self, item: dict) -> None:
        """
        Save the dataset to disk.
        """
        if s.ANALYSIS_VERBOSITY:
            self.logger.info( '{} - {} - DATASET FINAL -\n {} '.format(item['pair'], item['timeframe'], str(self.df)) + '-------'*20)

        self.df.sort_index(inplace=True, ascending=False)
        self.df.to_csv(self.final_file)

    def analyse(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Method that performs needed logic before actually performing analysis. """
        
        self.df = self.add_indicators(df=df)
        self.df = self.process_indicators(df=self.df)
        """
        try:
            df = self.add_indicators(df=df)
            try:
                df = self.process_indicators(df=df)
            except Exception as e:
                logger.exception('Exception occurred while processing indicators in analysis :: pair: ' + str(item.get('pair')) + ' ' + str(item.get('timeframe')), exc_info=e)
        except Exception as e:
            logger.exception('Exception occurred while adding indicators in analysis :: pair: ' + str(item.get('pair')) + ' ' + str(item.get('timeframe')), exc_info=e)
        """
        return self.df

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
        df['mfi_os'] = df.mfi < 20
        df['mfi_ob'] = df.mfi > 80
        df['rsi_os'] = df.rsi < 30
        df['rsi_ob'] = df.rsi > 70

        # Stoch Crossover SMRFI / MRFI
        df['slow_stoch_crossover_smrfi'] = self.crossover(df=df, crossing_col='slow_stoch', crossed_col='smrfi', new_col='slow_stoch_crossover_smrfi')
        df['slow_stoch_crossover_mrfi'] = self.crossover(df=df, crossing_col='slow_stoch', crossed_col='mrfi', new_col='slow_stoch_crossover_mrfi')
        df['slow_stoch14_crossover_smrfi'] = self.crossover(df=df, crossing_col='slow_stoch_sma14', crossed_col='smrfi', new_col='slow_stoch14_crossover_smrfi')
        df['slow_stoch14_crossover_mrfi'] = self.crossover(df=df, crossing_col='slow_stoch_sma14', crossed_col='mrfi', new_col='slow_stoch14_crossover_mrfi')
        df['slow_stoch26_crossover_smrfi'] = self.crossover(df=df, crossing_col='slow_stoch_sma26', crossed_col='smrfi', new_col='slow_stoch26_crossover_smrfi')
        df['slow_stoch26_crossover_mrfi'] = self.crossover(df=df, crossing_col='slow_stoch_sma26', crossed_col='mrfi', new_col='slow_stoch26_crossover_mrfi')

        # Stoch Crossunder SMRFI / MRFI
        df['slow_stoch_crossunder_smrfi'] = self.crossover(df=df, crossing_col='smrfi', crossed_col='slow_stoch', new_col='slow_stoch_crossunder_smrfi')
        df['slow_stoch_crossunder_mrfi'] = self.crossover(df=df, crossing_col='mrfi', crossed_col='slow_stoch', new_col='slow_stoch_crossunder_mrfi')
        df['slow_stoch14_crossunder_smrfi'] = self.crossover(df=df, crossing_col='smrfi', crossed_col='slow_stoch_sma14', new_col='slow_stoch14_crossunder_smrfi')
        df['slow_stoch14_crossunder_mrfi'] = self.crossover(df=df, crossing_col='mrfi', crossed_col='slow_stoch_sma14', new_col='slow_stoch14_crossunder_mrfi')
        df['slow_stoch26_crossunder_smrfi'] = self.crossover(df=df, crossing_col='smrfi', crossed_col='slow_stoch_sma26', new_col='slow_stoch26_crossunder_smrfi')
        df['slow_stoch26_crossunder_mrfi'] = self.crossover(df=df, crossing_col='mrfi', crossed_col='slow_stoch_sma26', new_col='slow_stoch26_crossunder_mrfi')

        return df

    def add_indicators(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Add indicators."""

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
        df['slow_stoch_sma26'] = df.slow_stoch.rolling(window=26).mean()

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
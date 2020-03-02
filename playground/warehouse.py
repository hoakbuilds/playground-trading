__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import threading
import time
import logging
import pandas as pd
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from typing import Any, Dict, List, Callable, Optional
from playground import enums
from playground import settings as s
from playground.analysis import Analyzer
from playground.cryptocompare import CryptoCompareAPI
from playground.pair import MarketPair
from playground.util import (
    setup_logger,
    timestamp_to_date,
)
from playground.util_ops import (
    get_cc_callable_by_def,
    get_delta_callable_for_tf,
    get_cc_callable_by_time,
)

class Warehouse:
    """Basic warehouse/persistence/db."""

    ready: bool = False

    updated: bool = False

    market_pairs: list = None

    missing_sets: list = None

    outdated_sets: list = None

    _cc: CryptoCompareAPI = None

    _verbose: bool = None
    _extra_verbose: bool = None

    __throttle: int = 5

    __rate_throttle: int = 2

    def __init__(self,):
        """
        Initialize the Warehouse object with the settings.
        """
        self.logger = setup_logger(name=__name__)
        self.logger.info('Initializing %s module.', __name__)

        self._parse_settings()

        self._parse_running_pairs()

        self.missing_sets = self._check_missing_datasets()

        if self.missing_sets:
            self._build_missing_datasets()

        self.set_ready()
        self.outdated_sets = self._check_outdated_datasets()
        
        if len(self.outdated_sets) == 0:
            self.logger.info('Warehouse ready and updated.')
            self.set_updated()
        
        self.update_datasets()

    def get_latest_candle(self, pair: MarketPair = None, timeframe: str = '') -> pd.DataFrame:
        """
        Fetch the last candle from a certain Pair and Timeframe.
        TODO: Pass OHLCV into a new class for better dot notation without indexing etc
        """
        dataset_file = s.DATASET_FOLDER + '{}_{}.csv'.format(pair, timeframe).replace(' ', '')

        try:
            _dataset = self._get_dataset_from_file(filename=dataset_file, rows=1)
        except:
            pass

        return _dataset

    def update_datasets(self):
        if not self.is_updated():
            helpers: list = []

            for item in self.outdated_sets:
                helper = threading.Thread(target=self._update_dataset, args=[item])
                helper.start()
                helpers.append(helper)
                if self._verbose:
                    self.logger.info('Updating dataset for {} {}..'.format(
                        item.get('pair'), item.get('timeframe').replace(' ', '')
                        )
                    )
                time.sleep(0.25)

            for helper in helpers:
                helper.join()

            self.logger.info('Warehouse updated..')

            self.outdated_sets = []
            self.set_updated()

            time.sleep(self.__throttle)

    def _keep_updated(self):
        
        self.logger.info('Keeping Warehouse updated...')

        self.outdated_sets = self._check_outdated_datasets()

        if len(self.outdated_sets) == 0:
            self.logger.info('Warehouse ready and updated.')
            self.set_updated()
        else:
            self.logger.info('Datasets outdated: {}'.format(self.outdated_sets))
            self.set_updating()
            self.update_datasets()

    def _update_dataset(self, config: Dict[str, Any]):
        """
        This function is used by the Warehouse to update the disk datasets with the newest data.
        The behavior of this method is designed this way because it is intended for both threaded and unthreaded use.
        Could be worse, could be better.
        """
        if self._extra_verbose:
            self.logger.info('Updating dataset %s %s.', config.get('pair'), config.get('timeframe').replace(' ', ''))

        if not self._cc:
            cc_config = {
                'comparison_symbol': str(config.get('pair').quote_currency)
            }
            self._cc = CryptoCompareAPI(config=cc_config, logger=self.logger, verbose=self._extra_verbose)

        api_call: Callable = None
        api_args: dict = None

        candle = self.get_latest_candle(pair=config.get('pair'), timeframe=config.get('timeframe'))

        (api_call, api_args) = get_cc_callable_by_time(cc=self._cc, config=config, candle=candle)
        
        # Fetch new data
        data = api_call(**api_args)
        new_data: list = data.get('Data', None)
        new_dataset: pd.DataFrame = pd.DataFrame(new_data)
        new_dataset['datetime'] = [dt.fromtimestamp(d) for d in new_dataset.time]
        new_dataset['timestamp'] = [d for d in new_dataset.time]
        new_dataset = new_dataset.set_index('time')

        # Fetch our disk dataset
        dataset_file = s.DATASET_FOLDER + '{}_{}.csv'.format(
            config.get('pair'), config.get('timeframe')).replace(' ', '')
        disk_dataset = self._get_dataset_from_file(filename=dataset_file,)
        disk_dataset = disk_dataset.set_index('time')

        # Join the data together and overwrite existing timeperiods with newest data
        newest_dataset: pd.DataFrame = disk_dataset.copy(deep=True)
        newest_dataset = newest_dataset.append(new_dataset, sort=False)
        newest_dataset = newest_dataset.drop_duplicates(subset='timestamp', keep='last')
        newest_dataset.sort_index(inplace=True, ascending=False)

        # Save the new data
        newest_dataset.to_csv(dataset_file)
        if self._extra_verbose:
            self.logger.info('Updated dataset %s %s.', config.get('pair'), config.get('timeframe').replace(' ', ''))

        return Analyzer.analyze(config, df=newest_dataset)


    def _build_dataset(self, config: Dict[str, Any]) -> pd.DataFrame:
        """
        This function is used by the Warehouse to build the missing datasets with data going as far as it can get.
        The behavior of this method is designed this way because it is intended for both threaded and unthreaded use.
        Could be worse, could be better.
        """

        if self._extra_verbose:
            self.logger.info('Building dataset for %s with interval %s.', config['pair'], config['timeframe'])

        if not self._cc:
            cc_config = {
                'comparison_symbol': str(config.get('pair').quote_currency)
            }
            self._cc = CryptoCompareAPI(config=cc_config, logger=self.logger, verbose=self._extra_verbose)

        initial_data: dict = None
        data: dict = None
        tf: str = config.get('timeframe')

        api_call: Callable = None
        api_args: dict = None

        api_call, api_args = get_cc_callable_by_def(config=config, cc=self._cc)

        while True:
            try:
                data = api_call(**api_args)
            except Exception as ex:
                self.logger.info('Connection with API is unstable. :: %s', ex)
                time.sleep(self.__throttle)
                continue

            if data:
                initial_data = data.get('Data', None)
                dataset: pd.DataFrame = pd.DataFrame(initial_data).set_index('time')
                if self._extra_verbose:
                    self.logger.info('Dataset Length: ' + str(len(dataset)))

                while True:
                    api_args =  {
                        'symbol': str(config.get('pair').base_currency),
                        'aggregate': int(config.get('timeframe').split(' ')[0]),
                        'limit': 2000,
                        'timestamp': data.get('TimeFrom', None),
                    }
                    try:
                        data = api_call(**api_args)
                    except Exception as ex:
                        self.logger.info('Connection with API is unstable. :: %s', ex)
                        time.sleep(self.__throttle)
                        continue

                    if data:
                        self.logger.info('Fetched dataset for %s - %s from ' + \
                            str(timestamp_to_date(data.get('TimeFrom', None)).date()) + ' to ' + \
                            str(timestamp_to_date(data.get('TimeTo', None)).date()), config['pair'], config['timeframe']
                        )
                        new_data: list = data.get('Data', None)
                        if new_data is not None and len(new_data) != 0:
                            if new_data[0]['high'] == 0 and new_data[0]['open'] == 0 and \
                                new_data[0]['low'] == 0 and  new_data[0]['close'] == 0 and new_data[0]['volumeto'] == 0:
                                break
                            df: pd.DataFrame = pd.DataFrame(new_data).set_index('time')
                            dataset = dataset.append(df, sort=False)
                            if self._extra_verbose:
                                self.logger.info('Dataset Length: ' + str(len(dataset)))
                        else:
                            break
                        time.sleep(self.__rate_throttle)
                    else:
                        break

            dataset.sort_index(inplace=True, ascending=False)
            dataset['datetime'] = [dt.fromtimestamp(d) for d in dataset.index]
            dataset['timestamp'] = [d for d in dataset.index]

            if self._extra_verbose:
                self.logger.info('DataFrame: ' + str(dataset.shape))

            dataset_file = s.DATASET_FOLDER + '{}_{}.csv'.format(config['pair'], config['timeframe']).replace(' ', '')
            dataset.to_csv(dataset_file)
            break

        return Analyzer.analyze(config, df=dataset)

    def _build_missing_datasets(self):
        """
        This function is used by the Warehouse to build the missing datasets with data going as far as it can get.
        """

        self.logger.info('Building datasets for: %s', self.missing_sets)

        helpers: list = []

        for item in self.missing_sets:
            helper = threading.Thread(target=self._build_dataset, args=[item])
            helper.start()
            helpers.append(helper)
            if self._verbose:
                self.logger.info('Building dataset for {} {}..'.format(
                    item.get('pair'), item.get('timeframe').replace(' ', '')
                    )
                )
            time.sleep(0.1)

        for helper in helpers:
            helper.join()

        self.logger.info('Warehouse ready..')
        self.missing_sets = []

        return self.set_ready()

    def _check_outdated_datasets(self):
        """
        This function is used by the Warehouse to check for outdated datasets.
        It will run inside the warehouse loop.
        """
        outdated_pair_tf: list = []

        for pair in self.market_pairs:
            for tf in s.TIMEFRAMES:
                candle = self.get_latest_candle(pair=pair, timeframe=tf)
                candle_time = dt.fromtimestamp(candle.time)
                current_time = dt.now()
                if self._extra_verbose:
                    self.logger.info('{} - Candle Time: {}'.format(str(str(pair)+' '+tf), candle_time))

                # rd stands for relativedelta
                rd_call: Callable = None
                rd_args: dict = None
                rd_call, rd_args = get_delta_callable_for_tf(tf=tf)
                delta = rd_call(**rd_args)
                next_candle = (candle_time + delta)

                if self._extra_verbose:
                    self.logger.info('{} - Next Time: {}'.format(str(str(pair)+' '+tf), next_candle))

                if current_time > next_candle:
                    outdated_pair_tf.append({
                        'pair': pair,
                        'timeframe': tf
                    })

        return outdated_pair_tf

    def _check_missing_datasets(self):

        missing_pair_tf: list = []

        for pair in self.market_pairs:
            for tf in s.TIMEFRAMES:
                dataset_file = s.DATASET_FOLDER + '{}_{}.csv'.format(pair, tf).replace(' ', '')

                if not self._get_dataset_from_file(
                        filename=dataset_file, exists=True,
                    ):
                    missing_pair_tf.append({
                        'pair': pair,
                        'timeframe': tf
                    })

        self.logger.info('Datasets missing: {}'.format(missing_pair_tf))
        
        return missing_pair_tf
        
    def _parse_settings(self,):

        self._verbose = s.WAREHOUSE_VERBOSITY
        self._extra_verbose = s.WAREHOUSE_EXTRA_VERBOSITY

    def _parse_running_pairs(self):

        self.logger.info('Configuring module.')

        market_pairs: list = []

        for pair in s.MARKET_PAIRS:
            market_pair = MarketPair(
                config=pair
            )
            market_pairs.append(market_pair)

        self.logger.info('Module found {} pairs:  {}'.format(len(market_pairs), market_pairs))

        self.market_pairs = market_pairs

    def _get_dataset_from_file(self, filename: str = None, exists: bool = False, rows: int = 0) -> Optional[pd.DataFrame]:
        """Fetches dataset from file by given filename."""
        if filename:
            dataset: pd.DataFrame = pd.DataFrame()
            try:
                if rows != 0:
                    dataset = pd.read_csv(filename, nrows=rows)
                else:
                    dataset = pd.read_csv(filename)
            except FileNotFoundError as ex:
                return None
            if exists:
                if dataset.empty:
                    return None
                else:
                    return True
            return dataset
        return None

    def set_ready(self,):
        """Used by the DataProvider to mark the warehouse as ready."""
        self.ready = True

    def is_ready(self,):
        """Used by the bot to check if the warehouse is updated."""
        return self.ready

    def set_updating(self,):
        """Used by the DataProvider to mark the warehouse as being updated."""
        self.updated = False

    def set_updated(self,):
        """Used by the DataProvider to mark the warehouse as updated."""
        self.updated = True

    def is_updated(self,):
        """Used by the bot to check if the warehouse is updated."""
        return self.updated
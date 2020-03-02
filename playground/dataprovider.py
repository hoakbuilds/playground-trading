__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import time
import logging
import pandas as pd
import threading
from typing import Dict, Any, Callable
from datetime import datetime as dt

from playground import settings as s
from playground.cryptocompare import CryptoCompareAPI
from playground.providerworker import ProviderWorkers
from playground.pair import MarketPair
from playground.util import setup_logger
from playground.warehouse import Warehouse
from playground.util_ops import get_cc_callable_by_time


class DataProvider:
    """Basic data provider."""

    # A list of workers for different timeframes
    workers: ProviderWorkers = None

    # This is the exchange's object
    # TODO: implement exhcnage class
    #exchange: Exchange

    _cc: CryptoCompareAPI = None

    _wh: Warehouse

    def __init__(self, warehouse: Warehouse, _daemon: bool = False):
        """
        Initialize the DataProvider object with the settings.
        """
        
        self.logger = setup_logger(name=__name__)

        self.logger.info('Initializing %s module.', __name__)

        self._cc = CryptoCompareAPI()

        self._wh = warehouse

        while not self._wh.is_ready():
            self.logger.info('Waiting for Warehouse...')
            time.sleep(2.5)
        

    def update_datasets(self, run_flag: bool = False):
        if not self._wh.is_updated():
            for item in self._wh.outdated_sets:
                self._update_dataset(dataset=item)

            self._wh.set_updated()
        elif run_flag:
            self._keep_updated()

    def _keep_updated(self):
        
        while True:
            self.logger.info('Keeping Warehouse updated...')

            self._wh.outdated_sets = self._wh._check_outdated_datasets()

            self.update_datasets()

            time.sleep(0.1)

    def _update_dataset(self, dataset: Dict[str, Any]):
        
        self.logger.info('Updating dataset %s %s.', dataset.get('pair'), dataset.get('timeframe').replace(' ', ''))

        if not self._cc:
            config = {
                'comparison_symbol': str(dataset.get('pair').quote_currency)
            }
            self._cc = CryptoCompareAPI(config=config, logger=self.logger)

        api_call: Callable = None
        api_args: dict = None

        candle = self._wh.get_latest_candle(pair=dataset.get('pair'), timeframe=dataset.get('timeframe'))

        (api_call, api_args) = get_cc_callable_by_time(cc=self._cc, config=dataset, candle=candle)
        
        # Fetch new data
        new_data = api_call(**api_args)
        new_dataset: pd.DataFrame = pd.DataFrame(new_data)
        new_dataset['timestamp'] = new_dataset.time
        new_dataset.set_index('time')

        # Fetch our disk dataset
        dataset_file = s.DATASET_FOLDER + '{}_{}.csv'.format(
            dataset.get('pair'), dataset.get('timeframe')).replace(' ', '')
        disk_dataset = self._wh._get_dataset_from_file(filename=dataset_file,)
        disk_dataset['timestamp'] = disk_dataset.time
        disk_dataset.set_index('time')

        # Join the data together and overwrite existing timeperiods with newest data
        newest_dataset: pd.DataFrame = disk_dataset.append(new_dataset, ignore_index=True)
        newest_dataset.set_index('timestamp')
        newest_dataset.sort_index(inplace=False, ascending=False)

        newest_dataset.to_csv(dataset_file)
        self.logger.info('Updated dataset %s %s.', dataset.get('pair'), dataset.get('timeframe').replace(' ', ''))

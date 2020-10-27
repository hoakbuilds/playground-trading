__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import threading
import time
import pandas as pd
from datetime import datetime as dt
from typing import Any, Dict, List, Callable, Optional
from playground import settings as s
from playground.analysis import Analyser
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
    """
    A csv-based warehousing absolute unit.
    """

    # Operating Logic
    ready: bool = False
    updated: bool = False
    analysed: bool = False

    # Assets on which to operate and check for missing and outdated datasets on startup
    market_pairs: List = None
    missing_sets: List = None
    missing_analysed_sets: List = None
    outdated_sets: List = None

    # Logging attributes
    _verbose: bool = None
    _extra_verbose: bool = None

    # Throttle attributes due to warehouse cycle and API limits etc
    __throttle: int = 2
    __rate_throttle: int = 1

    def __init__(self) -> None:
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

        self.outdated_sets = self._check_outdated_datasets()
        
        if len(self.outdated_sets) == 0:
            self.logger.info('Warehouse updated.')
            self.set_updated()
        else:
            self.logger.info('Datasets outdated: {}'.format(self.outdated_sets))
            self.update_datasets()

        if s.FORCE_STARTUP_ANALYSIS:
            self.logger.info('Forcing startup analysis.')
            self.analyse_datasets()

        self.missing_analysed_sets = self._check_missing_datasets(analysed=True)
        
        if len(self.missing_analysed_sets) == 0:
            self.logger.info('Warehouse analysed.')
            self.set_analysed()
        else:
            self.logger.info('Datasets outdated: {}'.format(self.outdated_sets))
            self.analyse_datasets(datasets=self.missing_analysed_sets) 
            # Only analyse the ones we detected earlier for less startup time
        
        self.set_ready()

    def get_latest_candle(
        self, pair: MarketPair = None, timeframe: str = '', analysed: bool = False, closed: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch the last candle from a certain Pair and Timeframe.

        Parameters `pair` and `timeframe` are mandatory.

        If `analysed` is passed, function will return the latest candle from the dataset post-analysis.
        If `closed` is passed, function will return the latest closed candle.

        :param `pair`: `MarketPair`
        :param `timeframe`: `str`
        :param `analysed`: `bool`
        :param `closed`: `bool`
        """

        dataset_file: str = ''
        if analysed:
            dataset_file = s.DATASET_FOLDER + '{}_{}_analyzed_v1.csv'.format(pair, timeframe).replace(' ', '')
        else:
            dataset_file = s.DATASET_FOLDER + '{}_{}.csv'.format(pair, timeframe).replace(' ', '')

        try:
            _dataset = self._get_dataset_from_file(filename=dataset_file, rows=1)
        except:
            dataset_file = s.DATASET_FOLDER + '{}_{}_analyzed.csv'.format(pair, timeframe).replace(' ', '')
            _dataset = self._get_dataset_from_file(filename=dataset_file, rows=s.MAX_ROWS)

        if closed:
            return _dataset.iloc[1]

        return _dataset.iloc[0]

    def get_dataset(self, pair: MarketPair = None, timeframe: str = '', analysed: bool = False, limit: int = None) -> pd.DataFrame:
        """
        Fetch the dataset up to the maximum number of rows as per config.

        Parameters `pair` and `timeframe` are mandatory.

        If `analysed` is passed, function will return the latest candle from the dataset post-analysis.

        :param `pair`: MarketPair that represents the pair to fetch
        :param `timeframe`: str that represents the timeframe, i.e. '5m', '1D'
        :param `analysed`: bool that represents if the dataset is analyzed or not
        :param `limit`: int that represents the limit of datapoints
        """

        dataset_file: str = ''
        if analysed:
            dataset_file = s.DATASET_FOLDER + '{}_{}_analyzed_v1.csv'.format(pair, timeframe).replace(' ', '')
        else:
            dataset_file = s.DATASET_FOLDER + '{}_{}.csv'.format(pair, timeframe).replace(' ', '')

        _dataset: pd.DataFrame = None
        
        if limit is None:
            try:
                _dataset = self._get_dataset_from_file(filename=dataset_file, rows=s.MAX_ROWS)
            except FileNotFoundError:
                dataset_file = s.DATASET_FOLDER + '{}_{}_analyzed.csv'.format(pair, timeframe).replace(' ', '')
                _dataset = self._get_dataset_from_file(filename=dataset_file, rows=s.MAX_ROWS)
            except KeyError:
                _dataset = self._get_dataset_from_file(filename=dataset_file, rows=s.MAX_ROWS)
        else:
            try:
                _dataset = self._get_dataset_from_file(filename=dataset_file, rows=limit)
            except FileNotFoundError:
                dataset_file = s.DATASET_FOLDER + '{}_{}_analyzed.csv'.format(pair, timeframe).replace(' ', '')
                _dataset = self._get_dataset_from_file(filename=dataset_file, rows=limit)
            except KeyError:
                _dataset = self._get_dataset_from_file(filename=dataset_file, rows=limit)

        return _dataset

    def update_datasets(self) -> None:
        """
        Analyse datasets.
        """

        if not self.is_updated():
            self.set_updating()
            helpers: list = []

            for item in self.outdated_sets:
                helper = threading.Thread(target=self._update_dataset, args=[item])
                helper.start()
                helpers.append(helper)
                if self._verbose:
                    self.logger.info('Updating and analysing dataset for {} {}..'.format(
                        item.get('pair'), item.get('timeframe').replace(' ', '')
                        )
                    )

            for helper in helpers:
                helper.join()

        self.outdated_sets = []
        self.set_updated()

    def analyse_datasets(self, datasets: list = None) -> None:
        """
        Analyse datasets.

        If `datasets` is passed, function will not use the market_pairs attribute.

        :param `datasets`: `list`
        """

        helpers: list = []
        self.set_analysing()

        if not datasets:
            for pair in self.market_pairs:
                for tf in s.WAREHOUSE_TIMEFRAMES:
                    item = {
                        'pair': pair,
                        'timeframe': tf
                    }
                    helper = threading.Thread(target=Analyser, args=[item])
                    helper.start()
                    helpers.append(helper)
                    if self._verbose:
                        self.logger.info('Re-analysing dataset for {} {}..'.format(
                            item.get('pair'), item.get('timeframe').replace(' ', '')
                            )
                        )
        else:
            for pair in datasets:
                for tf in s.WAREHOUSE_TIMEFRAMES:
                    item = {
                        'pair': pair,
                        'timeframe': tf
                    }
                    helper = threading.Thread(target=Analyser, args=[item])
                    helper.start()
                    helpers.append(helper)
                    if self._verbose:
                        self.logger.info('Analysing dataset for {} {}..'.format(
                            item.get('pair'), item.get('timeframe').replace(' ', '')
                            )
                        )

        for helper in helpers:
            helper.join()

        self.logger.info('Warehouse analysed..')

        if datasets:
            self.missing_analysed_sets = []

        self.set_analysed()

    def update(self) -> None:
        """
        This method needs to be called in a loop by a worker.
        """
        
        self.outdated_sets = self._check_outdated_datasets()

        if len(self.outdated_sets) == 0:
            self.logger.info('Warehouse remains updated.')
            self.set_updated()
        else:
            self.logger.info('Datasets outdated: {}'.format(self.outdated_sets))
            self.set_updating()
            self.update_datasets()
            self.logger.info('Warehouse successfully updated.')

    def _update_dataset(self, config: Dict[str, Any]) -> None:
        """
        This function is used by the Warehouse to update the disk datasets with the newest data.
        The behavior of this method is designed this way because it is intended for both threaded and unthreaded use.

        Param `config` is mandatory.

        Config follows the structured defined in the settings module.

        :param `config`: `dict`
        """
        if self._extra_verbose:
            self.logger.info('Updating dataset %s %s.', config.get('pair'), config.get('timeframe').replace(' ', ''))

        cc_config = {
            'comparison_symbol': str(config.get('pair').quote_currency),
            'apikey': str(config.get('pair')._api_key),
        }
        _cc: CryptoCompareAPI = CryptoCompareAPI(config=cc_config, logger=self.logger, verbose=self._extra_verbose)

        api_call: Callable = None
        api_args: dict = None

        candle = self.get_latest_candle(pair=config.get('pair'), timeframe=config.get('timeframe'))

        (api_call, api_args) = get_cc_callable_by_time(cc=_cc, config=config, candle=candle)
        # Fetch new data
        data = api_call(**api_args)
        new_data: list = data.get('Data', None)

        if new_data:
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
        else:
            self._build_dataset(config=config)

        return Analyser(item=config)

    def _build_dataset(self, config: Dict[str, Any]) -> pd.DataFrame:
        """
        This function is used by the Warehouse to build the missing datasets with data going as far as it can get.
        The behavior of this method is designed this way because it is intended for both threaded and unthreaded use.

        Param `config` is mandatory.

        Config follows the structured defined in the settings module.

        :param `config`: `dict`
        """

        if self._extra_verbose:
            self.logger.info('Building dataset for %s with interval %s.', config['pair'], config['timeframe'])

        cc_config = {
            'comparison_symbol': str(config.get('pair').quote_currency),
            'apikey': str(config.get('pair')._api_key),
        }
        _cc: CryptoCompareAPI = CryptoCompareAPI(config=cc_config, logger=self.logger, verbose=self._extra_verbose)

        initial_data: dict = None
        data: dict = None
        tf: str = config.get('timeframe')

        api_call: Callable = None
        api_args: dict = None

        api_call, api_args = get_cc_callable_by_def(config=config, cc=_cc)

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

        return Analyser(item=config)

    def _build_missing_datasets(self) -> None:
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

        for helper in helpers:
            helper.join()

        self.logger.info('Warehouse ready..')
        self.missing_sets = []

        return self.set_ready()

    def _check_outdated_datasets(self) -> list:
        """
        This function is used by the Warehouse to check for outdated datasets.
        It will run inside the warehouse loop.
        """
        outdated_pair_tf: list = []

        for pair in self.market_pairs:
            for tf in s.WAREHOUSE_TIMEFRAMES:
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

    def _check_missing_datasets(self, analysed: bool = False) -> list:
        """
        Checks for missing datasets.

        If `analysed` is passed, function will check for analysed datasets.

        :param `analysed`: `bool`
        """

        missing_pair_tf: list = []
        dataset_file: str = ''

        for pair in self.market_pairs:
            for tf in s.WAREHOUSE_TIMEFRAMES:
                if analysed:
                    dataset_file = s.DATASET_FOLDER + '{}_{}_analyzed_v1.csv'.format(pair, tf).replace(' ', '')
                else:
                    dataset_file = s.DATASET_FOLDER + '{}_{}.csv'.format(pair, tf).replace(' ', '')

                if not self._get_dataset_from_file(
                        filename=dataset_file, exists=True,
                    ):
                    missing_pair_tf.append({
                        'pair': pair,
                        'timeframe': tf
                    })

        if analysed:
            self.logger.info('Analysis datasets missing: {}'.format(missing_pair_tf))
        else:
            self.logger.info('Datasets missing: {}'.format(missing_pair_tf))

        return missing_pair_tf
        
    def _parse_settings(self) -> None:
        """
        Parse the warehouse's settings, such as logging, storage, etc..
        """

        self.logger.info('Parsing module settings.')
        self._verbose = s.WAREHOUSE_VERBOSITY
        self._extra_verbose = s.WAREHOUSE_EXTRA_VERBOSITY

    def _parse_running_pairs(self) -> None:
        """
        Parse the warehouse's running pairs and act accordingly.
        """

        self.logger.info('Parsing running pairs..')

        market_pairs: list = []

        for pair in s.MARKET_PAIRS:
            market_pair = MarketPair(
                config=pair
            )
            market_pairs.append(market_pair)

        self.logger.info('Module found {} pairs:  {}'.format(len(market_pairs), market_pairs))

        self.market_pairs = market_pairs

    def _get_dataset_from_file(
        self, filename: str = None, exists: bool = False, rows: int = 0,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch the dataset from a file with `filename`.

        Parameter `filename` is mandatory.

        If `exists` is passed, function will only check if the file exists or not and return the dataset.
        If `rows` is passed, function will only read `nrows=rows` from the file, default is 5000 as per settings.

        :param `filename`: `str`
        :param `exists`: `bool`
        :param `rows`: `int`
        """

        if filename:
            dataset: pd.DataFrame = pd.DataFrame()

            try:
                if rows != 0:
                    if rows == 1:
                        dataset = pd.read_csv(filename, nrows=(rows+1), error_bad_lines=False)
                        dataset.sort_index(inplace=True, ascending=True)
                    else:
                        dataset = pd.read_csv(filename, nrows=rows, error_bad_lines=False)
                        dataset.sort_index(inplace=True, ascending=False)
                else:
                    dataset = pd.read_csv(filename, error_bad_lines=False)
            except FileNotFoundError as ex:
                return None

            if exists:
                if dataset.empty:
                    return None
                else:
                    return True

            return dataset

        return None

    def set_ready(self,) -> None:
        """
        Used to mark the warehouse as ready.
        """
        self.ready = True

    def is_ready(self,) -> bool:
        """
        Used to check if the warehouse is updated.
        """
        return self.ready

    def set_updating(self,) -> None:
        """
        Used to mark the warehouse as being updated.
        """
        self.updated = False

    def set_updated(self,) -> None:
        """
        Used to mark the warehouse as updated.
        """
        self.updated = True

    def is_updated(self,) -> bool:
        """
        Used to check if the warehouse is updated.
        """
        return self.updated

    def set_analysing(self,) -> None:
        """
        Used to mark the warehouse as being analysed.
        """
        self.analysed = False

    def set_analysed(self,) -> None:
        """
        Used to mark the warehouse as analysed.
        """
        self.analysed = True

    def is_analysed(self,) -> bool:
        """
        Used to check if the warehouse is analysed.
        """
        return self.analysed

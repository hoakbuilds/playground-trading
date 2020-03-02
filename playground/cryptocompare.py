__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import logging
import pandas as pd
import requests 
from typing import List, Dict, Any, Optional
from datetime import datetime as dt
from playground import settings as s
from playground.util import setup_logger


class CryptoCompareAPI:
    """
    Early version of an adaptation of CryptoCompareAPI for early data mining
    """

    # This value represents the quote currency used to fetch data from the CCAPI
    comparison_symbol: str = None

    # This value represents the exchange used to fetch data from the CCAPI
    exchange: str = None

    _verbose: bool = None

    _header: dict = None

    def __init__(self, config: Dict[str, Any] = {}, logger: logging.Logger = None, verbose: bool = False):
        """
        Initialize the CryptoCompare API object with a Config dict.
        """

        if not logger:
            self.logger = setup_logger(name=__name__)
        else:
            self.logger = logger

        _api_key: str = config.get('apikey', None)
        self.comparison_symbol = config.get('comparison_symbol', 'USD')
        self.exchange = config.get('exchange', None)
        self._verbose = verbose

        if _api_key:
            self._header = {
                'Authorization': 'Apikey ' + _api_key,
            }
        elif s.CCAPI_KEY:
            self._header = {
                'Authorization': 'Apikey ' + s.CCAPI_KEY,
            }

        if self._verbose:
            self.logger.info('Initializing CryptoCompareAPI module with key {}.'.format(_api_key))


    def price(self, symbol: str, tsyms: list = None):
        """
        Fetch the price of a certain currency by `symbol`, using a certain
        """
        url = 'https://min-api.cryptocompare.com/data/price?fsym={}'\
                .format(symbol.upper())
        if tsyms:
            url += '&tsyms='
            for i, item in enumerate(tsyms):
                if i == len(tsyms):
                    url += '{}'.format(item)
                else:
                    url += '{},'.format(item)

        if self.exchange:
            url += '&e={}'.format(exchange)

        if self._verbose:
            self.logger.info('Requesting CryptoCompare:: {} ::'.format(url))

        if self._header:
            page = requests.get(url, headers=self._header)
        else:
            page = requests.get(url)

        data = page.json()
        return data


    def daily_price_full_data(self, symbol: str, compar):
        url = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsym={}'\
            .format(symbol.upper(), self.comparison_symbol.upper())

        if self._header:
            page = requests.get(url, headers=self._header)
        else:
            page = requests.get(url)

        if self._verbose:
            self.logger.info('Requesting CryptoCompare:: {} ::'.format(url))

        data = page.json()['Data']
        df = pd.DataFrame(data)
        df['timestamp'] = [dt.fromtimestamp(d) for d in df.time]
        return df


    def daily_price_historical(
        self, symbol: str, all_data: bool = False, limit: int = 1, aggregate: int = 1, timestamp: dt = None, comp_symbol: str = None,
    ):
        if timestamp:
            url = 'https://min-api.cryptocompare.com/data/histohday?fsym={}&limit=2000&aggregate={}&toTs={}'\
                    .format(symbol.upper(), aggregate, timestamp)
        else:
            url = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&limit={}&aggregate={}'\
                    .format(symbol.upper(), limit, aggregate)

        if comp_symbol:
            url += '&tsym={}'.format(comp_symbol.upper())
        else:
            url += '&tsym={}'.format(self.comparison_symbol.upper())

        if self.exchange:
            url += '&e={}'.format(self.exchange)
        if all_data:
            url += '&allData=true'

        if self._verbose:
            self.logger.info('Requesting CryptoCompare:: {} ::'.format(url))

        if self._header:
            page = requests.get(url, headers=self._header)
        else:
            page = requests.get(url)

        data = page.json()

        if data.get('Response', None) == 'Error':
            self.logger.info('Requested CryptoCompare:: {} :: {} :: {}'.format(url, page.status_code, data.get('Message', '')))
            return None

        if self._verbose:
            self.logger.info('Requested CryptoCompare:: {} :: {}'.format(url, page.status_code))

        if timestamp or limit == 2000:
            return data

        return data


    def hourly_price_historical(
        self, symbol: str, limit: int, aggregate: int, timestamp: dt = None, comp_symbol: str = None,
    ):
        if timestamp:
            url = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&limit=2000&aggregate={}&toTs={}'\
                    .format(symbol.upper(), aggregate, timestamp)
        else:
            url = 'https://min-api.cryptocompare.com/data/histohour?fsym={}&limit={}&aggregate={}'\
                    .format(symbol.upper(), limit, aggregate)

        if comp_symbol:
            url += '&tsym={}'.format(comp_symbol.upper())
        else:
            url += '&tsym={}'.format(self.comparison_symbol.upper())

        if self.exchange:
            url += '&e={}'.format(self.exchange)

        if self._verbose:
            self.logger.info('Requesting CryptoCompare:: {} ::'.format(url))

        if self._header:
            page = requests.get(url, headers=self._header)
        else:
            page = requests.get(url)

        data = page.json()

        if data.get('Response', None) == 'Error':
            self.logger.info('Requested CryptoCompare:: {} :: {} :: {}'.format(url, page.status_code, data.get('Message', '')))
            return None

        if self._verbose:
            self.logger.info('Requested CryptoCompare:: {} :: {}'.format(url, page.status_code))
        
        if timestamp or limit == 2000:
            return data

        return data


    def minute_price_historical(
        self, symbol: str, limit: int, aggregate: int, timestamp: dt = None, comp_symbol: str = None,
    ):
        if timestamp:
            url = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&limit=2000&aggregate={}&toTs={}'\
                    .format(symbol.upper(), aggregate, timestamp)
        else:
            url = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&limit={}&aggregate={}'\
                    .format(symbol.upper(), limit, aggregate)

        if comp_symbol:
            url += '&tsym={}'.format(comp_symbol.upper())
        else:
            url += '&tsym={}'.format(self.comparison_symbol.upper())

        if self.exchange:
            url += '&e={}'.format(self.exchange)

        if self._verbose:
            self.logger.info('Requesting CryptoCompare:: {} ::'.format(url))

        if self._header:
            page = requests.get(url, headers=self._header)
        else:
            page = requests.get(url)

        data = page.json()

        if data.get('Response', None) == 'Error':
            self.logger.info('Requested CryptoCompare:: {} :: {} :: {}'.format(url, page.status_code, data.get('Message', '')))
            return None

        if self._verbose:
            self.logger.info('Requested CryptoCompare:: {} :: {}'.format(url, page.status_code))

        if timestamp or limit == 2000:
            return data

        return data


    def coin_list(self): 
        url = 'https://min-api.cryptocompare.com/data/top/totalvolfull?limit=15&tsym=USD'

        if self._header:
            page = requests.get(url, headers=self._header)
        else:
            page = requests.get(url)

        data = page.json()['Data']
        return data


    def coin_snapshot_full_by_id(self, symbol: str, symbol_id_dict: dict):
        if not symbol_id_dict:
            symbol_id_dict = {
                'BTC': 1182,
                'ETH': 7605,
                'LTC': 3808
            }
        symbol_id = symbol_id_dict[symbol.upper()]
        url = 'https://www.cryptocompare.com/api/data/coinsnapshotfullbyid/?id={}'\
                .format(symbol_id)

        if self._header:
            page = requests.get(url, headers=self._header)
        else:
            page = requests.get(url)

        data = page.json()['Data']
        return data


    def live_social_status(self, symbol: str, symbol_id_dict: dict):
        if not symbol_id_dict:
            symbol_id_dict = {
                'BTC': 1182,
                'ETH': 7605,
                'LTC': 3808
            }
        symbol_id = symbol_id_dict[symbol.upper()]
        url = 'https://www.cryptocompare.com/api/data/socialstats/?id={}'\
                .format(symbol_id)

        if self._header:
            page = requests.get(url, headers=self._header)
        else:
            page = requests.get(url)

        data = page.json()['Data']
        return data
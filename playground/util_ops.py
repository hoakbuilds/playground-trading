__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import pandas as pd
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, Optional, Callable, Tuple
from playground import enums
from playground.cryptocompare import CryptoCompareAPI


def get_delta_callable_for_tf(tf: str = None) -> Optional[Tuple[Callable, Dict[str, Any]]]:
    """
    Returns a relativedelta callable and it's arguments for the timeframe.

    param: tf -- the timeframe object.
    """

    if tf is None:
        return None

    api_call: Callable = None
    api_args: dict = None

    if tf in str(enums.LOW_TIMEFRAMES):
        api_call = relativedelta
        api_args = {
            'minutes': int(tf.split(' ')[0])
        }
        
    elif tf in str(enums.MEDIUM_TIMEFRAMES):
        api_call = relativedelta
        api_args = {
            'hours': int(tf.split(' ')[0])
        }
        
    elif tf in str(enums.MACRO_TIMEFRAMES):
        api_call = relativedelta
        split = tf.split(' ')
        if split[1] == 'D':
            api_args = {
                'days': int(tf.split(' ')[0])
            }
        elif split[1] == 'W':
            api_args = {
                'weeks': int(tf.split(' ')[0])
            }
        elif split[1] == 'M':
            api_args = {
                'months': int(tf.split(' ')[0])
            }
        elif split[1] == 'Y':
            api_args = {
                'years': int(tf.split(' ')[0])
            }

    return (api_call, api_args)


def get_limit_for_candle_delta(candle: pd.DataFrame = None, config: Dict[str, Any] = None) -> Optional[int]:
    """
    Returns the amount of periods since the candle has closed.

    param: config -- the config of the running object.

    param: candle -- the last candle of the running object.
    """

    if candle is None:
        return None

    if config is None:
        return None
    
    tf: str = None
    tf = config.get('timeframe', None)
    if tf is None:
        return None

    current_time = dt.now()
    candle_time = dt.fromtimestamp(candle.timestamp)
    time_since = relativedelta(current_time, candle_time)

    split = tf.split()
    limit: int = 0
    time_period = int(split[0])

    if split[1] == 'm':
        if time_since.days != 0:
            limit += int((time_since.days * 1440) / time_period)

        if time_since.hours != 0:
            limit += int((time_since.hours * 60) / time_period)

        limit += int(time_since.minutes / time_period)

    elif split[1] == 'h':
        if time_since.days != 0:
            limit += int((time_since.days * 24) / time_period)

        limit += int(time_since.hours / time_period)

    elif split[1] == 'D':

        limit = int(time_since.days / time_period)

    elif split[1] == 'W':

        limit = int(time_since.weeks / time_period)

    elif split[1] == 'Y':
        limit = int(time_since.weeks / time_period)

    return int(limit)


def get_cc_callable_by_time(config: Dict[str, Any] = None, candle: pd.DataFrame = None, cc: CryptoCompareAPI = None) -> Optional[Tuple[Callable, Dict[str, Any]]]:
    """
    Returns a direct CCAPI callable and it's arguments for the passed candle based on time since passed.

    param: config -- the config of the running object.

    param: candle -- the last candle of the running object.

    param: cc -- the cryptocompareapi object.
    """

    if config is None:
        return None

    if candle is None:
        return None

    tf: str = None

    tf = config.get('timeframe', None)
    if tf is None:
        return None

    api_call: Callable = None
    api_args: dict = None
    limit: int = None

    limit = get_limit_for_candle_delta(config=config, candle=candle)
    if limit is None:
        return None

    if tf in str(enums.LOW_TIMEFRAMES):
        api_call = cc.minute_price_historical
        api_args = {
            'symbol': str(config.get('pair').base_currency),
            'aggregate': int(config.get('timeframe').split(' ')[0]),
            'limit': limit,
        }
    elif tf in str(enums.MEDIUM_TIMEFRAMES):
        api_call = cc.hourly_price_historical
        api_args =  {
            'symbol': str(config.get('pair').base_currency),
            'aggregate': int(config.get('timeframe').split(' ')[0]),
            'limit': limit,
        }
    elif tf in str(enums.MACRO_TIMEFRAMES):
        api_call = cc.daily_price_historical
        api_args =  {
            'symbol': str(config.get('pair').base_currency),
            'aggregate': int(config.get('timeframe').split(' ')[0]),
            'limit': limit,
        }

    return (api_call, api_args)


def get_cc_callable_by_def(config: Dict[str, Any] = None, cc: CryptoCompareAPI = None) -> Optional[Tuple[Callable, Dict[str, Any]]]:
    """
    Returns a direct CCAPI callable and it's arguments for the passed timeframe definition.

    param: config -- the config of the running object.

    param: cc -- the cryptocompareapi object.
    """
    if config is None:
        return None

    if cc is None:
        return None

    api_call: Callable = None
    api_args: dict = None
    tf: str = None

    tf = config.get('timeframe', None)
    if tf is None:
        return None

    if tf in str(enums.LOW_TIMEFRAMES):
        api_call = cc.minute_price_historical
        api_args = {
            'symbol': str(config.get('pair').base_currency),
            'aggregate': int(config.get('timeframe').split(' ')[0]),
            'limit': 2000,
        }
    elif tf in str(enums.MEDIUM_TIMEFRAMES):
        api_call = cc.hourly_price_historical
        api_args =  {
            'symbol': str(config.get('pair').base_currency),
            'aggregate': int(config.get('timeframe').split(' ')[0]),
            'limit': 2000,
        }
    elif tf in str(enums.MACRO_TIMEFRAMES):
        api_call = cc.daily_price_historical
        api_args =  {
            'symbol': str(config.get('pair').base_currency),
            'aggregate': int(config.get('timeframe').split(' ')[0]),
            'limit': 2000,
        }

    return (api_call, api_args)

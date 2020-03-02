__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import logging
import time
import requests
import csv
import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime as dt
from multiprocessing import Queue
from threading import Thread, Lock
from talib.abstract import *
from talib import MA_Type

from playground.dataprovider import Worker
from playground.notifiers import TwitterNotifier
from playground.analysis import add_indicators
from playground.util import timestamp_to_date

logger = logging.getLogger(__name__)


def build_btc_dataframe(minute: bool = False, hour: bool = False, day: bool = False):
    
    initial_data = request_cc_api(minute=minute, hour=hour, day=day)

    dataset: pd.DataFrame = pd.DataFrame(initial_data.get('Data', None)).set_index('time')
    data: dict = None
    print('Dataset Length: ' + str(len(dataset)))
    
    while True:
        if data is not None:
            print('Fetched dataset from ' + \
                str(timestamp_to_date(data.get('TimeFrom', None)).date()) + ' to ' + \
                str(timestamp_to_date(data.get('TimeFrom', None)).date()))

            data = request_cc_api(timestamp=data.get('TimeFrom', None), minute=minute, hour=hour, day=day)
        else:
            data = request_cc_api(timestamp=initial_data.get('TimeFrom', None), minute=minute, hour=hour, day=day)
        if data.get('Data', None):
            df = pd.DataFrame(data['Data']).set_index('time')
            #print('DataFrame: ' + str(df))

            dataset = dataset.append(df)
            #print('\n\n\nDataSet: ' + str(dataset))
            print('DataSet Length: ' + str(len(dataset)))
            time.sleep(0.1)
        else:
            break
    
    dataset.sort_index(inplace=True, ascending=True)
    dataset['time'] = [dt.fromtimestamp(d) for d in dataset.index]
    print('DataFrame: ' + str(dataset))

    # Save to csv before fiddling with indicators
    if day:
        dataset.to_csv('btc_cccagg_daily_raw.csv')

    if hour:
        dataset.to_csv('btc_cccagg_hourly_raw.csv')

    if minute:
        dataset.to_csv('btc_cccagg_minutely_raw.csv')

    return dataset.set_index('time')


def reorg_dataset(minute=False, hour=False, day=False):

    start = time.time()

    data = pd.DataFrame()
    # Save to csv before fiddling with indicators
    if day:
        data = pd.read_csv('btc_cccagg_daily_raw.csv')

    if hour:
        data = pd.read_csv('btc_cccagg_hourly_raw.csv')

    if minute:
        data = pd.read_csv('btc_cccagg_minutely_raw.csv')

    data = add_indicators(data).set_index('time')

    end = time.time()
    if day:
        data.to_csv('btc_cccagg_daily_indicators.csv')

    if hour:
        data.to_csv('btc_cccagg_hourly_indicators.csv')

    if minute:
        data.to_csv('btc_cccagg_minutely_indicators.csv')

    print('Shape: ' + str(data.shape) + '\n\n')
    print(data)
    print('\nTime to reorg dataset: ' + str(end - start))

    return data


def request_cc_api(timestamp=None, minute=False, hour=False, day=False, limit=None):

    if hour:
        if timestamp:
            url = 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=2000&toTs={}'.format(timestamp)
        elif limit:
            url = 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit={}'.format(limit)
        else:
            url = 'https://min-api.cryptocompare.com/data/v2/histohour?fsym=BTC&tsym=USD&limit=2000'
    
    if day:
        if timestamp:
            url = 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=2000&toTs={}'.format(timestamp)
        elif limit:
            url = 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit={}'.format(limit)
        else:
            url = 'https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=2000'
    
    if minute:
        if timestamp:
            url = 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=2000&toTs={}'.format(timestamp)
        elif limit:
            url = 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit={}'.format(limit)
        else:
            url = 'https://min-api.cryptocompare.com/data/v2/histominute?fsym=BTC&tsym=USD&limit=2000'

    
    page = requests.get(url)
    data = page.json()['Data']

    return data


def request_alternativeme_api_last_week():
    url = 'https://api.alternative.me/fng/?limit=2'
    res = [item for item in requests.get(url=url).json()['data']]
    return res


def request_alternativeme_api():
    url = 'https://api.alternative.me/fng/?limit=0'

    res = requests.get(url=url).json()
    return res


def maintain_dataset():

    twitter_notifier = TwitterNotifier()

    dataset = build_minute_dataset()

    try:
        while True:
            print(dataset)
            now = dt.utcnow()
            print('now: {}'.format(now))

            latest_candle = dataset.loc(0)
            print(latest_candle)

            latest_time = dt.fromtimestamp(latest_candle)

            print('now: {} - latest: {}'.format(now, latest_time))

            if latest_time != now:

                print('New candle.')
                data = request_cc_api(minute=True, limit=1)
                df = pd.DataFrame(data['Data']).set_index('time')
                dataset = dataset.append(df)
                dataset.sort_index(inplace=True, ascending=True)

                dataset = reorg_dataset(dataset)
                latest_candle = dataset.loc(len(dataset.index)-1)

                if latest_candle.touch_lower:
                    twitter_notifier.post_tweet(timeframe="1m", reason="your mom sends her regards. send her to namek. ")
            else:
                print('sleeping')
                time.sleep(5)
    
    except KeyboardInterrupt:
        print('Stopped.')
        

def build_minute_dataset(aggregate: int = 1):

    start = time.time()
    build_btc_dataframe(minute=True)
    end = time.time()

    print('Time to build {}M dataset: '.format(aggregate) + str(end - start))

    start = time.time()
    df = reorg_dataset(minute=True)
    end = time.time()
    
    print('Time to reorg + add indicators to M dataset: ' + str(end - start))

    return df


def build_hourly_dataset(aggregate: int = 1):

    start = time.time()
    build_btc_dataframe(hour=True)
    end = time.time()

    print('Time to build {}H dataset: '.format(aggregate) + str(end - start))

    start = time.time()
    reorg_dataset(hour=True)
    end = time.time()
    
    print('Time to reorg + add indicators to H dataset: ' + str(end - start))


def build_daily_dataset(aggregate: int = 1):

    start = time.time()
    build_btc_dataframe(day=True)
    end = time.time()

    print('Time to build {}D dataset: '.format(aggregate) + str(end - start))

    start = time.time()
    reorg_dataset(day=True)
    end = time.time()
    
    print('Time to reorg + add indicators to D dataset: ' + str(end - start))


if __name__ == '__main__':
    
    worker = Worker(config={
        'timeframe': '2m',
        'throttle': 120,
    })

    worker.run()

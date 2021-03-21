
__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import datetime
import time
import threading
from typing import Callable
from dateutil.relativedelta import relativedelta as rd
from datetime import datetime as dt
from playground import __version__, settings
from playground.abstract import Worker
from playground.util_ops import get_delta_callable_for_tf
from playground.warehouse.persistence import Warehouse


class WarehouseWorker(Worker):
    """Basic class for a main worker."""

    wh: Warehouse = None

    _next_candle_time: datetime.datetime = None

    __last_analysis: dt = None
    __analysis_throttle: int = 60
    __startup_throttle: int = 5

    def __init__(self, warehouse: Warehouse = None):
        """
        Init all variables and objects the worker needs.
        """
        super().__init__(
            name="WarehouseWorker",
            work_func=self.work,
            throttle_func=self._throttle_func,
        )

        if warehouse is None:
            raise Exception("WarehouseWorker class needs a warehouse to control")

        self.wh = warehouse

    def print_pair_candles(self):
        """
        Print available pair candles.
        """

        if not self.__last_analysis:
            self.__last_analysis = dt.now()

        current_time = dt.now()

        if current_time > (self.__last_analysis + rd(seconds=self.__analysis_throttle)):
            self.__last_analysis = dt.now()
            for pair in self.wh.market_pairs:
                for tf in settings.WAREHOUSE_TIMEFRAMES:
                    try:
                        _candle = self.wh.get_latest_candle(pair=pair, timeframe=tf, analysed=True, closed=True) # analysed candle

                        if settings.WORKER_VERBOSITY:
                            self.logger.info(
                                '%-5s - %-5s - %-5s - O: %-10.8g - H: %-10.8g - L: %-10.8g - C: %-10.8g - V: %-10.4g - MRFI:' \
                                    +' %-10.4g - SMRFI: %-10.4g - RSI: %-10.4g - MFI: %-10.4g - EMA50: %-10.4g - EMA100: %-10.4g ', \
                                    pair, tf, _candle.datetime, _candle.open, _candle.high, _candle.low, _candle.close,
                                    _candle.volumeto, _candle.mrfi, _candle.smrfi, _candle.rsi, _candle.mfi, _candle.ema50,
                                    _candle.ema100,
                            )
                    except:
                        pass

            return self.print_pair_crossovers()

    def print_candle_analysis(self, _candle, pair, tf):
        """ Receives a candle object and prints it's indicator analysis."""
        if _candle.ema20_50_cross:
            self.logger.info(
                '%-5s - %-5s - %-5s - EMA 20/50 CROSSOVER ', pair, tf, _candle.datetime,
            )

        if _candle.ema20_100_cross:
            self.logger.info(
                '%-5s - %-5s - %-5s - EMA 20/100 CROSSOVER ', pair, tf, _candle.datetime,
            )

        if _candle.ema50_100_cross:
            self.logger.info(
                '%-5s - %-5s - %-5s - EMA 50/100 CROSSOVER ', pair, tf, _candle.datetime,
            )
    
        if _candle.mrfi_ob:
            self.logger.info(
                '%-5s - %-5s - %-5s - MRFI OB ', pair, tf, _candle.datetime,
            )
    
        if _candle.mrfi_os:
            self.logger.info(
                '%-5s - %-5s - %-5s - MRFI OS ', pair, tf, _candle.datetime,
            )

        if _candle.smrfi_os:
            self.logger.info(
                '%-5s - %-5s - %-5s - SMRFI OB ', pair, tf, _candle.datetime,
            )

        if _candle.smrfi_os:
            self.logger.info(
                '%-5s - %-5s - %-5s - SMRFI OB ', pair, tf, _candle.datetime,
            )

        if _candle.touch_lower:
            self.logger.info(
                '%-5s - %-5s - %-5s - TOUCHING LOWER BOLLINGER BAND ', pair, tf, _candle.datetime,
            )
    
        if _candle.touch_upper:
            self.logger.info(
                '%-5s - %-5s - %-5s - TOUCHING UPPER BOLLINGER BAND ', pair, tf, _candle.datetime,
            )

        if _candle.crossing_dn:
            self.logger.info(
                '%-5s - %-5s - %-5s - CROSSING TO LOWER BOLLINGER BAND RANGE ', pair, tf, _candle.datetime,
            )

        if _candle.crossing_up:
            self.logger.info(
                '%-5s - %-5s - %-5s - CROSSING TO UPPER BOLLINGER BAND RANGE ', pair, tf, _candle.datetime,
            )

    def print_pair_crossovers(self):
        """
        Print available pair crossovers.
        """

        if not self.__last_analysis:
            self.__last_analysis = dt.now()

        current_time = dt.now()

        if current_time > (self.__last_analysis + rd(seconds=self.__analysis_throttle)):
            for pair in self.wh.market_pairs:
                for tf in settings.WAREHOUSE_TIMEFRAMES:
                    try:
                        _candle = self.wh.get_latest_candle(pair=pair, timeframe=tf, analysed=True, closed=True) # analysed candle
                        if settings.WORKER_VERBOSITY:
                            self.print_candle_analysis(_candle=_candle, pair=pair, tf=tf)
                    except:
                        pass

    def work(self):
        """
        Run the worker loop.
        """
        self.logger.info('Keeping Warehouse updated...')

        # Make sure the warehouse is updated
        self.wh.update()

        self._await_warehouse()
        
        if self.wh.is_analysed():
            self.print_pair_candles()

        candle = self.wh.get_latest_candle(
            pair=settings.MAIN_OPERATING_PAIR,
            timeframe=settings.MINIMUM_OPERATING_TIMEFRAME,
        )
        self._next_candle_time = dt.fromtimestamp(candle.time)
            
    def _throttle_func(self) -> int:
        """
        Returns an integer representing in seconds how long the warehouse will sleep.
        """
        # rd stands for relativedelta
        rd_call: Callable = None
        rd_args: dict = None
        rd_call, rd_args = get_delta_callable_for_tf(tf=settings.MINIMUM_OPERATING_TIMEFRAME)
        delta = rd_call(**rd_args)
        next_candle = (self._next_candle_time + delta)
        current_time = dt.now()
        time_left = (next_candle - current_time) 
        time_left = time_left.seconds + 1

        if settings.MINIMUM_OPERATING_TIMEFRAME == '1 m':
            if time_left > 60:
                time_left = 1
        elif settings.MINIMUM_OPERATING_TIMEFRAME == '5 m':
            if time_left > 300:
                time_left = 5
        self.logger.info(
            'MIN: %s | Sleeping for %ds | Active threads: %s', settings.MINIMUM_OPERATING_TIMEFRAME, time_left, str(threading.active_count())
        )
        return int(time_left)

    def _await_warehouse(self):
        """
        Awaits until the warehouse has gone from READY to ANALYSED.
        """

        while not self.wh.is_ready():
            time.sleep(self.__startup_throttle)
            self.logger.info('Waiting for the warehouse to be ready..')

        while not self.wh.is_updated():
            time.sleep(self.__startup_throttle)
            self.logger.info('Waiting for the warehouse to be updated..')

        while not self.wh.is_analysed():
            time.sleep(self.__startup_throttle)
            self.logger.info('Waiting for the warehouse to be analysed..')


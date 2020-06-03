__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import logging
import time
from dateutil.relativedelta import relativedelta as rd
from datetime import datetime as dt
from playground import __version__, settings
from playground.analysis import Analyser
from playground.api_server import ApiServer
from playground.enums import State
from playground.pair import MarketPair
from playground.simulation import ForwardTestSession
from playground.util import setup_logger
from playground.util_ops import get_delta_callable_for_tf
from playground.wallet import Wallet
from playground.warehouse import Warehouse
from playground import logic
#from playground.strategy import Strategy


class Worker:
    """Basic class for a main worker."""

    state: State = State.STOPPED

    api_srv: ApiServer = None
    wh: Warehouse = None
    wallet: Wallet = None

    forwardtests: list = None

    __throttle: int = 5
    __last_analysis: dt = None
    __analysis_throttle: int = 60
    __startup_throttle: int = 5

    def __init__(self):
        """
        Init all variables and objects the bot needs to work
        """
        self.logger = setup_logger(name=__name__)
        self.logger.info('Initializing %s module.', __name__)

        self.wh = Warehouse()

        # Await the Warehouse being ready and updated
        self._await_warehouse()

        self.logger.info('Parsing forwardtests and their strategies..')
        self.parse_forwardtesting()
        self.logger.info('Setting up notifiers...')

        # last thing to be up
        self.api_srv = ApiServer(self)

        # TODO: LIVE EXECUTION

        #self.logger.info('Parsing strategies..')
        #self.parse_strategies()

        #self.wallet = Wallet()

    def process_operating_forwardtests(self):
        """
        Process ongoing forwardtests.
        """

        for ft in self.forwardtests:
            _dataset = self.wh.get_dataset(pair=ft.pair, timeframe=ft.tf, analysed=True,)
            _candle = self.wh.get_latest_candle(pair=ft.pair, timeframe=ft.tf, analysed=True, closed=True)
            ft.update_dataset(dataset=_dataset)
            ft.process(today=_candle)

    def parse_forwardtesting(self):
        """
        Process available forwardtests.
        """
        self.forwardtests = []

        market_pairs: list = []

        for pair in settings.FT_MARKETPAIRS:
            market_pair = MarketPair(
                config=pair
            )
            market_pairs.append(market_pair)

        self.market_pairs = market_pairs

        self.logger.info('Module found {} pairs for FT:  {}'.format(len(market_pairs), market_pairs))

        for op_tf in settings.FT_TIMEFRAMES:
            for pair in self.market_pairs:
                self.logger.info('Launching FTS for: {} - {}'.format(pair, op_tf))
                _dataset = self.wh.get_dataset(pair=pair, timeframe=op_tf, analysed=True,)
                _candle = self.wh.get_latest_candle(pair=pair, timeframe=op_tf, analysed=True, closed=True) # analysed candle

                for strategy in pair.strategies:
                    strategy_function = getattr(logic, strategy)
                    ft: ForwardTestSession = ForwardTestSession(
                        data=_dataset,
                        yesterday=_candle,
                        initial_capital=settings.FT_INITIAL_CAPITAL[pair.wallet_currency],
                        pair=pair,
                        tf=op_tf,
                        logic=strategy_function,
                    )
                self.forwardtests.append(ft)

    def parse_strategies(self):
        """
        Process available strategies.
        for strategy in settings.strategies.
        """

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

    def print_status(self):
        """
        Show the worker status, this includes wallet balances, positions, etc.
        """

        balances = self.wallet.get_balances()

        for balance in balances:
            self.logger.info(
                '%s balance: %.2g | xbt : %.8g', balance.get('ticker'), balance.get('value'), balance.get('xbt_value'),
            )

    def run(self):
        """
        Run the worker loop.
        """

        while True:

            # Make sure the warehouse is updated
            self.wh._keep_updated()

            self._await_warehouse()
            
            if self.wh.is_analysed():
                self.print_pair_candles()

            #self.print_status()

            self.process_operating_forwardtests()

            candle = self.wh.get_latest_candle(
                pair=settings.MAIN_OPERATING_PAIR,
                timeframe=settings.MINIMUM_OPERATING_TIMEFRAME,
            )
            candle_time = dt.fromtimestamp(candle.time)
            current_time = dt.now()

            # rd stands for relativedelta
            rd_call: Callable = None
            rd_args: dict = None
            rd_call, rd_args = get_delta_callable_for_tf(tf=settings.MINIMUM_OPERATING_TIMEFRAME)
            delta = rd_call(**rd_args)
            next_candle = (candle_time + delta)

            time_left = (next_candle - current_time) 
            time_left = time_left.seconds + 1
            if settings.MINIMUM_OPERATING_TIMEFRAME == '1 m':
                if time_left > 60:
                    time_left = 1
            elif settings.MINIMUM_OPERATING_TIMEFRAME == '5 m':
                if time_left > 300:
                    time_left = 5
            self.logger.info(
                'MIN: %s | Sleeping for %ds', settings.MINIMUM_OPERATING_TIMEFRAME, time_left,
            )
            time.sleep(time_left)

    def _await_warehouse(self):

        while not self.wh.is_ready():
            time.sleep(self.__startup_throttle)
            self.logger.info('Waiting for the warehouse to be ready..')

        while not self.wh.is_updated():
            time.sleep(self.__startup_throttle)
            self.logger.info('Waiting for the warehouse to be updated..')

        while not self.wh.is_analysed():
            time.sleep(self.__startup_throttle)
            self.logger.info('Waiting for the warehouse to be analysed..')


__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import datetime
import logging
import time
import pandas as pd
from logging import Logger
from typing import Callable
from dateutil.relativedelta import relativedelta as rd
from datetime import datetime as dt
from playground import __version__, settings
from playground.analysis import Analyser
from playground.api_server import ApiServer
from playground.enums import State
from playground.models.pair import MarketPair
from playground.simulation import ForwardTestSession
from playground.util import setup_logger
from playground.util_ops import get_delta_callable_for_tf
from playground.wallet import Wallet
from playground.warehouse import Warehouse
from playground import logic
#from playground.strategy import Strategy



class ForwardtestEngine:

    def __init__(self, data: pd.DataFrame) -> None:
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas dataframe")

        self.logger = setup_logger(name=self._name)
        # rd stands for relativedelta
        rd_call: Callable = None
        rd_args: dict = None
        rd_call, rd_args = get_delta_callable_for_tf(tf=self.tf)
        self.__verbosity = settings.FORWARDTESTING_VERBOSITY
        self.__analysis_throttle = rd_call(**rd_args)
        self.__next_candle = (dt.fromtimestamp(self.yesterday.time) + self.__analysis_throttle)
        self.__next_analysis = (self.__next_candle + self.__analysis_throttle)
        self.__start_time = dt.now()
        self.logger.info('Forward testing session started for: {}-{} using {} at {} '.format(
            self.pair, self.tf, self.logic.__name__, self.__start_time,
            ),
        )
        self.logger.info('next analysis {}'.format(self.__next_analysis))


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
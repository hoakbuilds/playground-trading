__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import logging
import time
from playground import __version__, settings
from playground.analysis import Analyzer
from playground.api_server import ApiServer
from playground.dataprovider import DataProvider
from playground.enums import State
from playground.util import setup_logger
from playground.wallet import Wallet
from playground.warehouse import Warehouse
#from playground.strategy import Strategy


class Worker:
    """Basic class for a main worker."""

    state: State = State.STOPPED

    api_srv: ApiServer = None

    wh: Warehouse = None
 
    ta: Analyzer = None

    # TODO: pls yesnt
    #strategies: Strategy

    __throttle: int = 30
    __startup_throttle: int = 2

    def __init__(self):
        """
        Init all variables and objects the bot needs to work
        """
        self.logger = setup_logger(name=__name__)
        self.logger.info('Initializing %s module.', __name__)

        self.wh = Warehouse()

        self.logger.info('Parsing strategies..')
        self.parse_strategies()

        self.wallet = Wallet()

        self.logger.info('Setting up notifiers...')

        # last thing to be up
        self.api_srv = ApiServer(self)

    def parse_strategies(self):
        """
        Process available strategies.
        for strategy in settings.strategies.
        """

    def process_pairs(self):
        """
        Process available pairs.
        """

        for pair in self.wh.market_pairs:
            for tf in settings.TIMEFRAMES:
                candle = self.wh.get_latest_candle(pair=pair, timeframe=tf)
                if settings.WORKER_VERBOSITY:
                    self.logger.info(
                        '%s - %s - O: %d - H: %d - L: %d - C: %d - V: %d ', \
                            pair, tf, candle.open[0], candle.high[0], candle.low[0], candle.close[0], candle.volumeto[0] # noqa
                        )

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

        # Await the Warehouse being ready and updated
        self._wait_warehouse()

        while True:

            # Make sure the warehouse is updated
            self.wh._keep_updated()

            self.process_pairs()

            self.logger.info('Analyzing..')

            #self.print_status()

            time.sleep(self.__throttle)          


    def _wait_warehouse(self):

        while not self.wh.is_ready(): 
            time.sleep(self.__startup_throttle)
            self.logger.info('Waiting for the warehouse to be ready..')

        while not self.wh.is_updated():
            time.sleep(self.__startup_throttle)
            self.logger.info('Waiting for the warehouse to be updated..')


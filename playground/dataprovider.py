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

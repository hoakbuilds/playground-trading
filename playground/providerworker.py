__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import threading
from typing import Dict, Any, List
from playground.pair import MarketPair
from playground.warehouse import Warehouse
from playground.util import setup_logger


class ProviderWorker:
    """Basic worker for data provider."""

    last_candle: Dict

    timeframe: str

    throttle: int

    _wh: Warehouse

    def __init__(self, config: Dict[str, Any], warehouse: Warehouse, pair: MarketPair):
        """
        Initialize the ProviderWorker object with the settings.
        """

        self.logger = setup_logger(name=__name__)
        self.logger.info('Initializing {} for {}.'.format(__name__, pair))

        self._wh = warehouse

        self.last_candle = None

    def run(self):
        logger.info('starting dataprovider worker s')


class ProviderWorkers:
    """Advanced control of workers for iteration etc."""

    num_workers: int = 0

    _list: List[ProviderWorker] = None

    def __init__(self):
        pass

    def __iter__(self):
        return iter(self._list)

    def new(self, config: Dict[str, Any], warehouse: Warehouse, pair: MarketPair):
        
        if not self._list:
            self._list =  []

        worker = ProviderWorker(config=config, warehouse=warehouse, pair=pair)

        worker_thread = threading.Thread(target=worker.run)

        self._list.append(worker)
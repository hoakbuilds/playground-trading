__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from datetime import datetime
import time
import threading
import datetime as dt
from logging import Logger
from typing import Callable
from playground import __version__
from playground.util import setup_logger
from playground.models.pair import MarketPair


class Operation:
    """
    Base class for an operation.

    param: name -- the operation name.
    param: market_pair -- the market_pair to operate on.

    param: work_func -- the Callable that performs the worker's job.
    param: throttle_func -- the Callable that is used to calculate throttle time.
    """

    # Critical
    logger: Logger
    name: str = None
    desired_start: dt.datetime = None
    desired_finish: dt.datetime = None
    pair: MarketPair = None
    timeframe: str = None

    def __init__(self,
        name: str = None, market_pair: MarketPair = None, timeframe: str =  None,
        desired_start: dt.datetime = None, desired_finish: dt.datetime = None,
        work_func: Callable = None, throttle_func: Callable = None,) -> None:
        """
        Initialize the worker.
        """
        if name is None:
            raise Exception("Operation class needs `name` param to designate itself")

        if market_pair is None:
            raise Exception("Operation class needs `market_pair` param to work on")

        if timeframe is None:
            raise Exception("Operation class needs `timeframe` param to work on")

        self.name = '{}.{}-{}-{}'.format(__name__, name, market_pair, timeframe)
        self.logger = setup_logger(name=self.name)
        self.logger.info('Initializing %s operation.', self.name)

        if desired_start is None:
            raise Exception("Operation class needs `desired_start` param to work on")

        if desired_finish is None:
            raise Exception("Operation class needs `desired_finish` param to work on")

        self.pair = market_pair

    def get_desired_start(self) -> dt.datetime:
        """
        Get the datetime object that represents the desired start date.
        """
        return self.desired_start
        
    def get_desired_finish(self) -> dt.datetime:
        """
        Get the datetime object that represents the desired finished date.
        """
        return self.desired_finish

    def get_pair(self) -> MarketPair:
        """
        Get the market pair object associated.
        """
        return self.pair
        
    @staticmethod
    def from_json(json = None):
        """
        Return the object from json
        """
        return Operation(
            name=json.get('name', None),
            market_pair=MarketPair.from_json(json.get('market_pair', None)),
            timeframe=json.get('timeframe', None),
            desired_start=datetime.strptime(json.get('desired_start', None)),
            desired_finish=datetime.strptime(json.get('desired_finish', None)),
        )
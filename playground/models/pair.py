__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import logging
from typing import List, Dict, Any
from playground.enums import *
from playground.util import setup_logger

logger = setup_logger(name=__name__)

class Currency:
    """
    This class represents a Currency
    """

    # This value represents the currency's ticker, e.g. $BTC, $USD $EUR
    ticker: str = None

    # This value represents the currency's name, e.g Bitcoin, Dollar, Euro
    name: str = None


    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Init from json

        :param config: json dict of the class
        """
        ticker = config.get('ticker', '')
        name = config.get('name', '')
        if name is None:
            raise Exception("Currency class needs `name` param")

        if ticker is None:
            raise Exception("Currency class needs `ticker` param")
        self.ticker = ticker
        self.name = name

    def __str__(self) -> str:
        """String representation."""
        return '{}'.format(self.ticker)

    def __repr__(self) -> str:
        """String representation."""
        return '${}'.format(self.ticker)


class MarketPair:
    """
    This class represents a Market Pair
    """

    # This is the base currency of the pair, e.g in BTC/USD it would be BTC
    base_currency: Currency = None

    # This is the quote currency of the pair, e.g in BTC/USD it would be USD
    quote_currency: Currency = None

    # This value represents the wallet currency's name, e.g Bitcoin, Dollar, Euro
    wallet_currency: str = None

    # This value represents the market pair's applied strategies
    strategies: list = None

    # Pairs with their exclusive key
    _api_key: str = None

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Init from json

        :param config: json dict of the class
        """
        base_currency = config.get('base_currency', '')
        quote_currency = config.get('quote_currency', '')
        if base_currency is None:
            raise Exception("MarketPair class needs `base_currency` param")

        if quote_currency is None:
            raise Exception("MarketPair class needs `quote_currency` param")

        self.base_currency = Currency(config=base_currency)
        self.quote_currency = Currency(config=quote_currency)
        self.wallet_currency = config.get('wallet_currency', '')
        self.strategies = config.get('strategies')
        self.exchange = config.get('exchange', '')
        self._api_key = config.get('apikey', None)
        if self._api_key:
            logger.info('Pair {}{} with exclusive CCAPI_KEY:: {}'.format(self.base_currency, self.quote_currency, self._api_key))

    def __str__(self) -> str:
        """String representation."""
        return '{}{}'.format(self.base_currency, self.quote_currency)

    def __repr__(self) -> str:
        """String representation."""
        return '{}/{}'.format(self.base_currency, self.quote_currency)

    @staticmethod
    def from_json(json: Dict[str, Any] = None):
        """
        Return the object from json
        """
        return MarketPair(config=json)
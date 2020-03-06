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
        self.ticker = config.get('ticker', '')
        self.name = config.get('name', '')

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

    _api_key: str = None

    def __init__(self, config: Dict[str, Any]) -> None:
        # TODO exchange class
        self.exchange = config.get('exchange', '')
        self._api_key = config.get('apikey', None)
        self.base_currency = Currency(config = config.get('base_currency', None))
        self.quote_currency = Currency(config = config.get('quote_currency', None))
        if self._api_key:
            logger.info('Pair {}{} with exclusive CCAPI_KEY:: {}'.format(self.base_currency, self.quote_currency, self._api_key))

    def __str__(self) -> str:
        """String representation."""
        return '{}{}'.format(self.base_currency, self.quote_currency)

    def __repr__(self) -> str:
        """String representation."""
        return '{}/{}'.format(self.base_currency, self.quote_currency)

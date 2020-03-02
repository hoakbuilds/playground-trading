__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from settings_local import *

# ######### operation settings ######### #
# General DEBUG, for maximum efficiency set to `True` and point all verbosity vars to it

DEBUG = True

# This setting defines if the warehouse should log extra verbosely

WORKER_VERBOSITY = False
CRYPTOCOMPARE_VERBOSITY = DEBUG
WAREHOUSE_EXTRA_VERBOSITY = False
WAREHOUSE_VERBOSITY = False
DATASET_FOLDER = 'data/'

# ######### dry execution parameters ######### #

PREF_XBT_FIAT = 'USD'

INITIAL_CAPITAL = [
    {
        'currency': {
            'ticker': 'USD',
            'name': 'dolla dolla bill',
        },
        'initial_balance': 10000,
        'apikey': CCAPI_KEY,
    },
    {
        'currency': {
            'ticker': 'EUR',
            'name': 'jjust euro things',
        },
        'initial_balance': 10000,
        'apikey': CCAPI_KEY,
    },
    {
        'currency': {
            'ticker': 'BTC',
            'name': 'Bitcoin',
        },
        'initial_balance': 0.10000000,
        'apikey': CCAPI_KEY,
    },
]

# ######### operating timeframes ######### #

TIMEFRAMES = [
    '3 m', '5 m','15 m', '30 m', '1 h', '4 h', '1 D', '3 D',
]

# ######### operating market pairs ######### #

MARKET_PAIRS = [
    {
        'base_currency': {
            'ticker': 'BTC',
            'name': 'Bitcoin',
        },
        'quote_currency': {
            'ticker': 'USD',
            'name': 'dolla dolla bill',
        },
        'apikey': CCAPI_KEY_BTCUSD,
    },
    {
        'base_currency': {
            'ticker': 'ETH',
            'name': 'etHerioeunm',
        },
        'quote_currency': {
            'ticker': 'USD',
            'name': 'dolla dolla bill',
        },
        'apikey': CCAPI_KEY_ETHUSD,
    },
    {
        'base_currency': {
            'ticker': 'XTZ',
            'name': 'tezzies',
        },
        'quote_currency': {
            'ticker': 'USD',
            'name': 'dolla dolla bill',
        },
        'apikey': CCAPI_KEY_XTZUSD,
    },
    {
        'base_currency': {
            'ticker': 'XRP',
            'name': 'XRPONZO',
        },
        'quote_currency': {
            'ticker': 'USD',
            'name': 'dolla dolla bill',
        },
        'apikey': CCAPI_KEY_XRPUSD,
    },
    {
        'base_currency': {
            'ticker': 'ETH',
            'name': 'etHerioeunm',
        },
        'quote_currency': {
            'ticker': 'BTC',
            'name': 'Bitcoin',
        },
        'apikey': CCAPI_KEY_ETHBTC,
    },
]

__all__ = [
    CCAPI_KEY, CONSUMER_KEY, CONSUMER_SECRET,
    ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
]
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
WORKER_VERBOSITY = DEBUG
CRYPTOCOMPARE_VERBOSITY = False
WAREHOUSE_EXTRA_VERBOSITY = False
WAREHOUSE_VERBOSITY = DEBUG
DATASET_FOLDER = 'data/'

# ######### dry execution parameters ######### #

INITIAL_CAPITAL = [
    {
        'currency': {
            'ticker': 'USD',
            'name': 'dolla dolla bill',
        },
        'initial_balance': 10000,
    },
    {
        'currency': {
            'ticker': 'BTC',
            'name': 'Bitcoin',
        },
        'initial_balance': 0.10000000,
    },
]

# ######### operating timeframes ######### #

TIMEFRAMES = [
    '5 m','15 m', '1 m', '1 h', '4 h', '1 D', '3 D',
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
    },
]


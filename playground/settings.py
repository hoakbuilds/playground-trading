__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from settings.settings_local import *

###############################################
# ########## LOGGING CONFIGURATION ########## #
###############################################

DEBUG = True

CRYPTOCOMPARE_VERBOSITY = False
ANALYSIS_VERBOSITY = False
WORKER_EXTRA_VERBOSITY = False
WORKER_VERBOSITY = False
WAREHOUSE_EXTRA_VERBOSITY = False
WAREHOUSE_VERBOSITY = False
BACKTESTING_VERBOSITY = DEBUG
FORWARDTESTING_VERBOSITY = DEBUG

###############################################
# ########## LIVE EXECUTION CONFIGURATION ########## # TODO: DO IT, IT'S WRONG
###############################################

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

###############################################
# ######### WAREHOUSE CONFIGURATION ######### #
###############################################

# ######### general parameters ############## #


# ######### analysis parameter ############## #

FORCE_STARTUP_ANALYSIS = False
MAX_ROWS = 5000

# ########## operating timeframes ########### #

WAREHOUSE_TIMEFRAMES = [
    '5 m','15 m', '30 m', '1 h', '4 h', '1 D', '3 D',
]

# ######### operating market pairs ########## #

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
    {
        'base_currency': {
            'ticker': 'XRP',
            'name': 'XRPONZO',
        },
        'quote_currency': {
            'ticker': 'BTC',
            'name': 'Bitcoin',
        },
        'apikey': CCAPI_KEY_XRPBTC,
    },
    {
        'base_currency': {
            'ticker': 'LTC',
            'name': 'litecona',
        },
        'quote_currency': {
            'ticker': 'BTC',
            'name': 'Bitcoin',
        },
        'apikey': CCAPI_KEY_LTCBTC,
    }
]

###############################################
# ###### FORWARDTESTING CONFIGURATION ####### #
###############################################

FT_INITIAL_CAPITAL = {
    'BTC': 0.1,
    'USD': 10000,
    'EUR': 10000,
}

MINIMUM_OPERATING_TIMEFRAME = '5 m'
MAIN_OPERATING_PAIR = 'BTCUSD'

FT_MARKETPAIRS = [
    {
        'base_currency': {
            'ticker': 'BTC',
            'name': 'Bitcoin',
        },
        'quote_currency': {
            'ticker': 'USD',
            'name': 'dolla dolla bill',
        },
        'wallet_currency': 'USD',
        'strategies': [
            'chopfucker_v1',
        ]
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
        'wallet_currency': 'USD',
        'strategies': [
            'strategy_v1',
        ]
    }
]

FT_TIMEFRAMES = [
   '5 m', '15 m', '30 m', '1 h', '4 h', '1 D'
]

__all__ = [
    CCAPI_KEY, CONSUMER_KEY, CONSUMER_SECRET,
    ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
]
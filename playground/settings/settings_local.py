###############################################
# ######### WAREHOUSE CONFIGURATION ######### #
###############################################

# ######### general parameters ############## #

BASE_FOLDER = '/envs/playground-data'
DATASET_FOLDER = '{}/data/'.format(BASE_FOLDER)
CHARTS_FOLDER = '{}/charts/'.format(BASE_FOLDER)
BACKTESTS_CHARTS_FOLDER = CHARTS_FOLDER + '{}/'.format('backtests')
FORWARDTESTS_CHARTS_FOLDER = CHARTS_FOLDER + '{}/'.format('forwardtests')

# ############### API CONFIGURATIONS ############### #

# ########## COIN MARKET CAP PRO API KEY ########### #
CMC_PRO_API_KEY = 'api-key'

# ######### CRYPTOCOMPARE API KEY ###### #
# default key in case of not tracking 1min dataset (44k calls/mo)
CCAPI_KEY = 'api-key'

# pair-specific API keys in case of tracking the 1min dataset + others

# USD PAIRS #
CCAPI_KEY_BTCUSD  = 'api-key'
CCAPI_KEY_ETHUSD  = 'api-key'
CCAPI_KEY_XTZUSD  = 'api-key'
CCAPI_KEY_LINKUSD = 'api-key'
CCAPI_KEY_XRPUSD  = 'api-key'
CCAPI_KEY_LTCUSD  = 'api-key'

# BTC PAIRS #
CCAPI_KEY_ETHBTC = 'api-key'
CCAPI_KEY_LTCBTC = 'api-key'
CCAPI_KEY_TRXBTC = 'api-key'
CCAPI_KEY_XRPBTC = 'api-key'


# ######### TWITTER ######### #
CONSUMER_SECRET = 'api-key'
CONSUMER_KEY = 'api-key'

ACCESS_TOKEN = 'api-key'
ACCESS_TOKEN_SECRET = 'api-key'
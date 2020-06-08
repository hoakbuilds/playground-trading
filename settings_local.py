
###############################################
# ######### WAREHOUSE CONFIGURATION ######### #
###############################################

# ######### general parameters ############## #

BASE_FOLDER = 'path/to/your/data/folder'
DATASET_FOLDER = '{}/data/'.format(BASE_FOLDER)
CHARTS_FOLDER = '{}/charts/'.format(BASE_FOLDER)
BACKTESTS_CHARTS_FOLDER = CHARTS_FOLDER + '{}/'.format('backtests')
FORWARDTESTS_CHARTS_FOLDER = CHARTS_FOLDER + '{}/'.format('forwardtests')

# ############### API CONFIGURATIONS ############### #

# ########## COIN MARKET CAP PRO API KEY ########### #
# used for some global data
CMC_PRO_API_KEY = 'cmc_pro_api_key' 

# ######### CRYPTOCOMPARE API KEY ###### #
# default key in case of not tracking 1min dataset (44k calls/mo)
CCAPI_KEY = 'ccapi_key'

# pair-specific API keys in case of tracking the 1min dataset + others

# USD PAIRS #
CCAPI_KEY_BTCUSD  = 'ccapi_key_pair_1'
CCAPI_KEY_ETHUSD  = 'ccapi_key_pair_2'
CCAPI_KEY_XTZUSD  = 'ccapi_key_pair_3'
CCAPI_KEY_LINKUSD = 'ccapi_key_pair_4'
CCAPI_KEY_XRPUSD  = 'ccapi_key_pair_5'
CCAPI_KEY_LTCUSD  = 'ccapi_key_pair_6'

# BTC PAIRS #
CCAPI_KEY_ETHBTC = 'ccapi_key_pair_7'
CCAPI_KEY_LTCBTC = 'ccapi_key_pair_8'
CCAPI_KEY_TRXBTC = 'ccapi_key_pair_9'
CCAPI_KEY_XRPBTC = 'ccapi_key_pair_10'


# ######### TWITTER ######### #
CONSUMER_SECRET = 'twitter_consumer_secret'
CONSUMER_KEY = 'twitter_consumer_key'

ACCESS_TOKEN = 'twitter_access_token'
ACCESS_TOKEN_SECRET = 'twitter_access_token_secret'

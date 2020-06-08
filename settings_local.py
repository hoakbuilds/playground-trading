
###############################################
# ######### WAREHOUSE CONFIGURATION ######### #
###############################################

# ######### general parameters ############## #

BASE_FOLDER = '/envs/playground-data/'
DATASET_FOLDER = '{}/data/'.format(BASE_FOLDER)
CHARTS_FOLDER = '{}/charts/'.format(BASE_FOLDER)
BACKTESTS_CHARTS_FOLDER = CHARTS_FOLDER + '{}/'.format('backtests')
FORWARDTESTS_CHARTS_FOLDER = CHARTS_FOLDER + '{}/'.format('forwardtests')

# ############### API CONFIGURATIONS ############### #

# ########## COIN MARKET CAP PRO API KEY ########### #
# used for some global data
CMC_PRO_API_KEY = '770d19e3-b391-4e99-8e48-67dfcf10d508' 

# ######### CRYPTOCOMPARE API KEY ###### #
# default key in case of not tracking 1min dataset (44k calls/mo)
CCAPI_KEY = 'e0a25ef4356a791930d551c667978659c56031cc2d1527aa4c8c8aee74f18a82'

# pair-specific API keys in case of tracking the 1min dataset + others

# USD PAIRS #
CCAPI_KEY_BTCUSD  = '5fc1c96274a3a9eba10d40a32bbc748a0bfc202394dd687bc2029610998017f6'
CCAPI_KEY_ETHUSD  = '5e7ee58e47f8aaf0dbb3b099a2442339875fae236f11bb50a2381305b69c6aa2'
CCAPI_KEY_XTZUSD  = 'd78694e68d327c6b767b1571092d0bba361e0ae7af6d5213639f2ebc708ed29e'
CCAPI_KEY_LINKUSD = 'caba1f0da560024d4c43122114b2723cce20a877a47c6a388df4fe8de36f134e'
CCAPI_KEY_XRPUSD  = 'e094138ed189dce1310f0928d510cc182f43ca1f5b39a669b0757031f9b90f1d'
CCAPI_KEY_LTCUSD  = '0e4e13fc6e4cb73b6d1f17f95eb82c23a955bb58a2f8fb03c236fbf5eea229f7'

# BTC PAIRS #
CCAPI_KEY_ETHBTC = 'bc03e3ad3106b6ba61d8212f95f313a555792e0400e504f1d3d772de9d8dd7ae'
CCAPI_KEY_LTCBTC = '11b6d7e06f59f6bbee70e19d277c99307fb3a0c21b047c76f96b64990efa9991'
CCAPI_KEY_TRXBTC = '60210783283e735e3d897c5511b4a15aabb42616dff83ae2d73e36544de94462'
CCAPI_KEY_XRPBTC = '052e4236632051777a00122609e5d7ec3570074f90ddad863ca9399aef722cca'


# ######### TWITTER ######### #
CONSUMER_SECRET = 'lkcRgPmbf6Yk9StOdJIDzKwCOMBC3yjWtVmlHuqTOxESzzPEGq'
CONSUMER_KEY = 'MSqgDlAlPQvuQIj1sLpgln0V4'

ACCESS_TOKEN = '1216046823066030080-18xeUQh8GeomlsVco52yz4HlNnosp4'
ACCESS_TOKEN_SECRET = 'hrIKiSIRdUPQ7B1sZtOsBkssDnyWzmSrnAgCzDq8yfeEA'

__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from playground import settings
from playground.cryptocompare import CryptoCompareAPI
from playground.pair import Currency
from playground.util import setup_logger


class Wallet:
    """Basic wallet class."""

    wallet_balances: list = None

    available_balances: list = None

    margin_balances: list = None

    def __init__(self):
        """Initialize the wallet module."""
        self.logger = setup_logger(name=__name__)
        self.logger.info('Initializing %s module.', __name__)

        self.wallet_balances = self._setup_wallet()

        for item in self.wallet_balances:
            currency = item.get('currency')
            if currency and str(currency) == 'BTC':
                self.logger.info('Initial wallet balance for %s: %.8g', currency, item.get('value'))
            else:
                self.logger.info('Initial wallet balance for %s: %d', currency, item.get('value'))

    def _setup_wallet(self) -> list:

        _wallet_balances: list = []

        for item in settings.INITIAL_CAPITAL:
            currency = item.get('currency')
            cc_config = {
                'comparison_symbol': str(currency.get('ticker')),
                'apikey': str(item.get('apikey')),
            }
            obj = {
                'currency': Currency(config=item.get('currency')),
                'value': item.get('initial_balance'),
                'cc': CryptoCompareAPI(config=cc_config),
            }
            _wallet_balances.append(obj)

        return _wallet_balances

    def get_balances(self) -> list:
        """Return list of wallet balances."""
        
        _balances: list = []
        _cv: dict = self._get_currency_values()
        for balance in self.wallet_balances:
            _value: float = float(balance.get('value'))
            _currency = balance.get('currency')
            obj: dict = {}

            if _currency.ticker != 'BTC':
                obj = {
                    'ticker': _currency.ticker,
                    'value': _value,
                    'xbt_value': _fiat_to_xbt(fiat_amount=_value, btc_value=_cv.get(_currency.ticker)),
                }
                _balances.append(obj)
            elif _currency.ticker == 'BTC':
                obj = {
                    'ticker': _currency.ticker,
                    'value': _value,
                    'xbt_value': _xbt_to_fiat(xbt_amount=_value, btc_value=_cv.get(settings.PREF_XBT_FIAT)),
                }
                _balances.append(obj)

        return _balances


    def _get_currency_values(self) -> dict:
        """
        Convert btc to eur based on inputs. only works for btc atm.
        """
        _tsyms: list = []

        for balance in self.wallet_balances:
            cc: CryptoCompareAPI = None
            currency = balance.get('currency')

            if currency.ticker != 'BTC':
                _tsyms.append(currency.ticker)
            else:
                cc = balance.get('cc')
            
        currency_value = cc.price(symbol=currency.ticker, tsyms=_tsyms)
        
        return currency_value

def _fiat_to_xbt(fiat_amount: float = None, btc_value: float = None) -> float:
    """Just a thing lol."""
    return float(fiat_amount/float(btc_value))

def _xbt_to_fiat(xbt_amount: float = None, btc_value: float = None) -> float:
    """Just a thing lol."""
    return float(xbt_amount * float(btc_value))
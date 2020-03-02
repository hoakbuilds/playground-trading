__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"


from playground import settings
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

    def _setup_wallet(self) -> dict:

        wallet_balances: list = []

        for item in settings.INITIAL_CAPITAL:
            obj = {
                'currency': Currency(config=item.get('currency')),
                'value': item.get('initial_balance'),
            }
            wallet_balances.append(obj)

        return wallet_balances
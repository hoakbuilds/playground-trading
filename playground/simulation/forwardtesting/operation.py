__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from datetime import datetime as dt
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta as rd
from typing import Callable, ForwardRef

# Local imorts
from playground import settings
from playground.notifiers import TwitterNotifier
from playground.simulation import Account, helpers
from playground.util import setup_logger
from playground.util_ops import get_delta_callable_for_tf
from playground.enums import RunMode


class ForwardTestingOperation:
    """An object representing the Backtesting Operation."""


    def __init__(self, config, ):
        """Initate the SimulationEngine.
        param: config: An HLOCV+ pandas dataframe with a datetime index
        type: config: pandas.DataFrame
        """  

        self.logger.info('next anBacktestingOperationalysis {}'.format(self.__next_analysis))

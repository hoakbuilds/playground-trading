__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import datetime as dt
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta as rd
from typing import Callable

# Local imorts
from playground import settings
from playground.util import setup_logger
from playground.util_ops import get_delta_callable_for_tf
from playground.enums import RunMode


class SimulatedOperationConfig:
    """An object representing the Simulated Operation."""

    def __init__(self, ):
        """Simply return the corresponding type's SimulatedOp class
        param: config: A SimulatedOperationConfig
        type: config: SimulatedOperationConfig
        """

        return 

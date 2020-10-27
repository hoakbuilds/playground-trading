__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime
from playground import enums


def timestamp_to_date(timestamp=None):
    """
    Convert timestamp to datetime object
    """
    return datetime.fromtimestamp(int(timestamp))


def setup_logger(name: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    return logger


class ArgumentDebugger:
    """
    Class used to debug passed args and kwargs into a determined function
    """

    @staticmethod
    def print_kwargs(**kwargs):
            print(kwargs)

    @staticmethod
    def print_values(**kwargs):
        for key, value in kwargs.items():
            print("The value of {} is {}".format(key, value))

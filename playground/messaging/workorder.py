__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from typing import Dict, Any
from playground.enums import *
from playground.util import setup_logger
from playground.messaging import Stream

logger = setup_logger(name=__name__)


class WorkOrder:
    """
    This class represents a WorkOrder
    """

    # This is the base currency of the pair, e.g in BTC/USD it would be BTC
    name: str = None


    def __init__(self, ) -> None:
        """
        Init from json

        :param config: json dict of the class
        """

    def __str__(self) -> str:
        """String representation."""
        return '[{}-{}]'.format(self.name, self.stream)

def from_json(json: Dict[str, Any] = None):
    """
    Return the object from json
    """
    return WorkOrder(config=json)
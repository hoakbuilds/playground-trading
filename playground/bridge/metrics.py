__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

# Global imports
from typing import Any, Dict, List, Optional

# Local imports
from playground.util import setup_logger
from playground.abstract.metrics import Metrics


class BridgeMetrics(Metrics):
    """An object representing the BridgeMetrics."""

    def __init__(self,):
        """
        Simply initiate the BridgeMetrics.
        """
        super().__init__(
            name="BridgeMetrics",
        )
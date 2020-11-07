__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

# Global imports
from logging import Logger
from typing import Any, Dict, List, Optional

# Local imports
from playground.util import setup_logger


class Metrics:
    """An object representing the BridgeConfig."""

    logger: Logger = None
    name: str = None
    messages_read: int = None
    messages_delivered: int = None

    def __init__(self, name: str = None):
        """
        Simply initiate the BridgeConfig.
        """

        if name is None:
            raise Exception("Metrics class needs `name` param to designate itself")

        self.name = '{}.{}'.format(__name__, name)
        logger = setup_logger(name=self.name)

        logger.info('Initializing %s component.', self.name)

        # Set all metrics to 0
        self.messages_read = 0
        self.messages_delivered = 0
    
    def increment_messages_read(self,) -> None:
        """
        Incremments messages read.
        """
        self.messages_read = self.messages_read + 1

    def increment_messages_delivered(self,) -> None:
        """
        Incremments messages delivered.
        """
        self.messages_delivered = self.messages_delivered + 1
    
    def get_metrics(self,) -> Dict[str, Any]:
        """
        Return the metrics as a dict.
        """
        return {
            'messages_read': self.messages_read,
            'messages_delivered': self.messages_delivered,
        }